from typing import Any, Dict, List, Optional
from django.db import transaction
from django.contrib.auth.models import User
from django.urls import reverse
from apps.core.services import CoreService
from .models import Order, OrderItem


class OrderService:
    """Service class for order lifecycle management."""

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
        payment_method: str = 'full',
        payment_status: str = 'chua_thanh_toan',
        note: str = ""
    ) -> Order:
        """
        Handles order creation logic including stock validation and deduction.
        """
        total_amount = float(sum(
            item["price"] * item.get("quantity", 1) for item in cart_items
        )) - float(discount_amount)
        
        if total_amount < 0:
            total_amount = 0
 
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
            note=note
        )

        from apps.products.models import Product

        for item in cart_items:
            quantity = item.get("quantity", 1)
            # Use select_for_update to handle concurrency and lock the product row
            product = Product.objects.select_for_update().get(id=item["product_id"])

            if product.stock < quantity:
                raise ValueError(
                    f"Sản phẩm '{product.name}' không đủ tồn kho (hiện còn {product.stock})."
                )

            product.stock -= quantity
            product.save()

            OrderItem.objects.create(
                order=order, product=product, quantity=quantity, price=item["price"]
            )

        # Gửi thông báo cho Admin khi có đơn hàng mới
        admins = User.objects.filter(is_superuser=True)
        order_url = reverse('orders:order_detail', args=[order.id])
        for admin in admins:
            CoreService.create_notification(
                recipient=admin,
                title="Đơn đặt hàng mới",
                message=f"Khách hàng {full_name} vừa đặt một đơn hàng mới (Mã: {order.order_code}).",
                link=order_url
            )

        return order

    @staticmethod
    def handle_order_action(
        order: Order, 
        action: str, 
        staff_id: str = "",
        cancel_reason: str = "",
        proof_image=None,
        user=None
    ) -> Order:
        """
        Updates order status and manages staff assignments/tasks directly on the Order model.
        """
        if action == "assign_staff":
            if staff_id:
                try:
                    staff = User.objects.get(id=staff_id)
                    order.assigned_staff = staff
                    order.status = "confirmed"
                    
                    # Notify Staff
                    if staff:
                        order_url = reverse('orders:order_detail', args=[order.id])
                        CoreService.create_notification(
                            recipient=staff,
                            title="Nhiệm vụ mới: Nhận việc",
                            message=f"Bạn vừa được giao nhận việc cho đơn hàng {order.order_code}. Vui lòng kiểm tra và bắt đầu xử lý.",
                            link=order_url
                        )
                except (User.DoesNotExist, ValueError):
                    pass
        elif action == "start_shipping":
            order.status = "processing"
        elif action == "complete":
            order.status = "completed"
            order.payment_status = "da_thanh_toan" # Auto-set to paid on completion
            if proof_image:
                order.proof_image = proof_image
        elif action == "cancel":
            order.status = "cancelled"
            if cancel_reason:
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
        
        # Notify Customer on status change
        if action in ["assign_staff", "start_shipping", "complete", "cancel"] and order.customer:
            status_text = {
                "assign_staff": "đã được xác nhận",
                "start_shipping": "đang được giao/xử lý",
                "complete": "đã hoàn thành",
                "cancel": "đã bị hủy"
            }.get(action, "")
            
            customer_url = reverse('purchase_detail', args=[order.id])
            CoreService.create_notification(
                recipient=order.customer,
                title="Cập nhật đơn hàng",
                message=f"Đơn hàng {order.order_code} của bạn {status_text}.",
                link=customer_url
            )

        # Notify Admin when staff completes order
        if action == "complete":
            admins = User.objects.filter(is_superuser=True)
            order_url = reverse('orders:order_detail', args=[order.id])
            staff_name = order.assigned_staff.get_full_name() or order.assigned_staff.username if order.assigned_staff else "Nhân viên"
            for admin in admins:
                CoreService.create_notification(
                    recipient=admin,
                    title="Xác nhận hoàn thành đơn hàng",
                    message=f"Nhân viên {staff_name} đã hoàn thành đơn hàng {order.order_code}. Vui lòng kiểm tra ảnh minh chứng và đối soát.",
                    link=order_url
                )

        # Notify Admin and Staff if customer cancels
        if action == "cancel" and user == order.customer:
            admins = User.objects.filter(is_superuser=True)
            order_url = reverse('orders:order_detail', args=[order.id])
            for admin in admins:
                CoreService.create_notification(
                    recipient=admin,
                    title="Khách hàng hủy đơn",
                    message=f"Đơn hàng {order.order_code} đã bị khách hàng {order.full_name} hủy. Lý do: {cancel_reason}",
                    link=order_url
                )
            if order.assigned_staff:
                CoreService.create_notification(
                    recipient=order.assigned_staff,
                    title="Đơn hàng bị hủy",
                    message=f"Đơn hàng {order.order_code} bạn đang phụ trách đã bị khách hàng hủy.",
                    link=order_url
                )

        return order

    @staticmethod
    def calc_current_step(order: Order) -> int:
        """Calculates the current step index for the order progress bar."""
        status_steps = ["pending", "confirmed", "processing", "completed"]
        if order.status in status_steps:
            return status_steps.index(order.status)
        return 0
