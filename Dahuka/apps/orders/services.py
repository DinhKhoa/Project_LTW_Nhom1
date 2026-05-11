from typing import Any, Dict, List, Optional
from django.db import transaction
from django.contrib.auth.models import User
from django.urls import reverse
from apps.core.services import CoreService
from .models import Order, OrderItem

# ==============================================================================
# SERVICE LAYER: XỬ LÝ NGHIỆP VỤ ĐƠN HÀNG (BUSINESS LOGIC)
# ==============================================================================

class OrderService:

    @staticmethod
    @transaction.atomic
    def create_order(
        customer: Optional[User],
        full_name: str,
        phone: str,
        cart_items: List[Dict[str, Any]],
        city: str = "",
        district: str = "",
        ward: str = "",
        house_details: str = "",
        discount_amount: float = 0,
        deposit_amount: float = 0,
        payment_method: str = "full",
        payment_status: str = "chua_thanh_toan",
        note: str = "",
    ) -> Order:
        """
        Quy trình tạo đơn hàng mới: 
        1. Tính tổng tiền -> 2. Lưu Order -> 3. Kiểm tra & Trừ kho -> 4. Tạo OrderItem -> 5. Gửi thông báo.
        @transaction.atomic: Đảm bảo nếu bước 3 lỗi thì bước 2 sẽ bị hủy bỏ (Rollback).
        """
        # --- BƯỚC 1: TÍNH TỔNG GIÁ TRỊ ĐƠN HÀNG ---
        total_amount = float(
            sum(item["price"] * item.get("quantity", 1) for item in cart_items)
        ) - float(discount_amount)

        if total_amount < 0:
            total_amount = 0

        # --- BƯỚC 2: KHỞI TẠO ĐƠN HÀNG CHÍNH ---
        order = Order.objects.create(
            customer=customer,
            full_name=full_name,
            phone=phone,
            city=city,
            district=district,
            ward=ward,
            house_details=house_details,
            total_amount=total_amount,
            deposit_amount=deposit_amount,
            status="pending",
            payment_method=payment_method,
            payment_status=payment_status,
            note=note,
        )

        from apps.products.models import Product

        # --- BƯỚC 3: XỬ LÝ CHI TIẾT SẢN PHẨM & TỒN KHO ---
        for item in cart_items:
            quantity = item.get("quantity", 1)
            
            # select_for_update(): Khoá hàng này trong DB để tránh 2 người cùng mua cái cuối cùng (Race Condition prevention)
            product = Product.objects.select_for_update().get(id=item["product_id"])

            if product.stock < quantity:
                raise ValueError(
                    f"Sản phẩm '{product.name}' không đủ tồn kho (hiện còn {product.stock})."
                )

            # Trừ số lượng tồn kho
            product.stock -= quantity
            product.save()

            # Tạo bản ghi chi tiết
            OrderItem.objects.create(
                order=order, product=product, quantity=quantity, price=item["price"]
            )

        # --- BƯỚC 4: GỬI THÔNG BÁO CHO ADMIN ---
        admins = User.objects.filter(is_superuser=True)
        order_url = reverse("orders:order_detail", args=[order.id])
        for admin in admins:
            CoreService.create_notification(
                recipient=admin,
                title="Đơn đặt hàng mới",
                message=f"Khách hàng {full_name} vừa đặt một đơn hàng mới (Mã: {order.order_code}).",
                link=order_url,
            )

        return order

    @staticmethod
    def process_warranty(order: Order) -> None:
        """
        Tự động tính toán ngày hết hạn bảo hành dựa trên chuỗi văn bản trong Product spec.
        VD: "24 tháng" -> cộng 24 tháng vào ngày hiện tại.
        """
        import re
        from django.utils import timezone
        import datetime

        items = order.items.all()
        for item in items:
            if not item.warranty_expiration:
                months = 24 # Mặc định 2 năm nếu không ghi gì
                if item.product and item.product.spec_warranty:
                    warranty_str = item.product.spec_warranty.lower()
                    # Sử dụng Regex để tìm số trong chuỗi (VD: "24 tháng" -> lấy số 24)
                    numbers = re.findall(r"\d+", warranty_str)
                    if numbers:
                        val = int(numbers[0])
                        # Nếu ghi "năm" thì nhân với 12 để quy đổi ra tháng
                        if "năm" in warranty_str or "nam" in warranty_str:
                            val *= 12
                        months = val

                try:
                    current_time = timezone.localtime()
                    # Cộng năm/tháng vào ngày hiện tại
                    if months % 12 == 0:
                        years = months // 12
                        item.warranty_expiration = current_time.replace(
                            year=current_time.year + years
                        )
                    else:
                        item.warranty_expiration = current_time + datetime.timedelta(
                            days=int(months * 30.44)
                        )
                except Exception:
                    item.warranty_expiration = (
                        timezone.localtime() + datetime.timedelta(days=months * 30)
                    )

                item.save()

    @staticmethod
    def handle_order_action(
        order: Order,
        action: str,
        staff_id: str = "",
        cancel_reason: str = "",
        proof_image=None,
        user=None,
    ) -> Order:
        """
        Cơ chế Máy trạng thái (State Machine) điều khiển vòng đời đơn hàng.
        Xử lý: Giao việc -> Giao hàng -> Hoàn thành -> Hủy.
        """
        
        # 1. Giao việc cho nhân viên
        if action == "assign_staff":
            if staff_id:
                try:
                    staff = User.objects.get(id=staff_id)
                    order.assigned_staff = staff
                    order.status = "confirmed"

                    if staff:
                        # Sửa link dẫn đến app tasks dành cho nhân viên (không phải orders dành cho admin)
                        order_url = reverse("tasks:task_detail", args=[order.id])
                        CoreService.create_notification(
                            recipient=staff,
                            title="Nhiệm vụ mới: Nhận việc",
                            message=f"Bạn vừa được giao nhận việc cho đơn hàng {order.order_code}.",
                            link=order_url,
                        )
                except (User.DoesNotExist, ValueError):
                    pass
        
        # 2. Bắt đầu giao hàng
        elif action == "start_shipping":
            order.status = "processing"
            
        # 3. Hoàn thành đơn hàng (Thu tiền & Kích hoạt bảo hành)
        elif action == "complete":
            order.status = "completed"
            order.payment_status = "da_thanh_toan"
            if proof_image:
                order.proof_image = proof_image

            # Tự động tính ngày bảo hành cho từng sản phẩm
            OrderService.process_warranty(order)

        # 4. Hủy đơn hàng
        elif action == "cancel":
            order.status = "cancelled"
            if cancel_reason:
                # Ghi lại ai là người đã hủy đơn
                if user:
                    if user.is_staff or user.is_superuser:
                        user_info = "Dahuka"
                    elif user == order.customer:
                        user_info = "Khách hàng"
                    else:
                        user_info = user.get_full_name() or user.username
                else:
                    user_info = "Hệ thống"
                order.cancel_reason = f"{user_info} đã hủy: {cancel_reason}"

        order.save()

        # --- GỬI THÔNG BÁO CẬP NHẬT CHO KHÁCH HÀNG ---
        if (
            action in ["assign_staff", "start_shipping", "complete", "cancel"]
            and order.customer
        ):
            status_text = {
                "assign_staff": "đã được xác nhận",
                "start_shipping": "đang được giao/xử lý",
                "complete": "đã hoàn thành",
                "cancel": "đã bị hủy",
            }.get(action, "")

            # Cần thêm namespace 'account:' vì URL này thuộc app account
            customer_url = reverse("account:purchase_detail", args=[order.id])
            CoreService.create_notification(
                recipient=order.customer,
                title="Cập nhật đơn hàng",
                message=f"Đơn hàng {order.order_code} của bạn {status_text}.",
                link=customer_url,
            )

        # Thông báo cho Admin khi nhân viên hoàn thành việc
        if action == "complete":
            admins = User.objects.filter(is_superuser=True)
            order_url = reverse("orders:order_detail", args=[order.id])
            staff_name = (
                order.assigned_staff.get_full_name() or order.assigned_staff.username
                if order.assigned_staff
                else "Nhân viên"
            )
            for admin in admins:
                CoreService.create_notification(
                    recipient=admin,
                    title="Xác nhận hoàn thành đơn hàng",
                    message=f"Nhân viên {staff_name} đã hoàn thành đơn hàng {order.order_code}. Vui lòng kiểm tra đối soát.",
                    link=order_url,
                )

        if action == "cancel" and user == order.customer:
            admins = User.objects.filter(is_superuser=True)
            order_url = reverse("orders:order_detail", args=[order.id])
            for admin in admins:
                CoreService.create_notification(
                    recipient=admin,
                    title="Khách hàng hủy đơn",
                    message=f"Đơn hàng {order.order_code} đã bị khách hàng {order.full_name} hủy. Lý do: {cancel_reason}",
                    link=order_url,
                )
            if order.assigned_staff:
                # Sửa link dẫn đến app tasks dành cho nhân viên
                staff_url = reverse("tasks:task_detail", args=[order.id])
                CoreService.create_notification(
                    recipient=order.assigned_staff,
                    title="Đơn hàng bị hủy",
                    message=f"Đơn hàng {order.order_code} bạn đang phụ trách đã bị khách hàng hủy.",
                    link=staff_url,
                )

        return order

    @staticmethod
    def calc_current_step(order: Order) -> int:
        """Trả về chỉ số bước hiện tại (0-3) để vẽ thanh tiến trình trên giao diện."""
        status_steps = ["pending", "confirmed", "processing", "completed"]
        if order.status in status_steps:
            return status_steps.index(order.status)
        return 0
