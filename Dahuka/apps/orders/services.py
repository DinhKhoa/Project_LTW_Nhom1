from django.core.paginator import Paginator
from django.db.models import Q
from .models import Order, OrderItem
from django.contrib.auth.models import User
from apps.core.constants import DEFAULT_PAGE_SIZE

from django.db import transaction


class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order(customer, full_name, phone, cart_items, city="", district="", ward="", house_details="", discount_amount=0, hinh_thuc_thanh_toan='chuyen_khoan', trang_thai_thanh_toan='chua_thanh_toan'):
        total_amount = sum(
            item["price"] * item.get("quantity", 1) for item in cart_items
        ) - discount_amount
        
        if total_amount < 0: total_amount = 0

        order = Order.objects.create(
            customer=customer,
            full_name=full_name,
            phone=phone,
            city=city,
            district=district,
            ward=ward,
            house_details=house_details,
            total_amount=total_amount,
            status="pending",
            hinh_thuc_thanh_toan=hinh_thuc_thanh_toan,
            trang_thai_thanh_toan=trang_thai_thanh_toan,
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

        return order

    @staticmethod
    def get_orders(query="", status_filter="", page_number=1, per_page=None, user=None):
        if per_page is None:
            per_page = DEFAULT_PAGE_SIZE
        orders = Order.objects.all()

        if user and not user.is_staff:
            orders = orders.filter(customer=user)

        if query:
            orders = orders.filter(
                Q(id__icontains=query)
                | Q(full_name__icontains=query)
                | Q(phone__icontains=query)
            )

        if status_filter:
            orders = orders.filter(status=status_filter)

        orders = orders.order_by("-created_at")
        paginator = Paginator(orders, per_page)
        return paginator.get_page(page_number)

    @staticmethod
    def handle_order_action(order, action, staff_id=""):
        if action == "confirm":
            order.status = "confirmed"
        elif action == "start_shipping":
            order.status = "processing"
        elif action == "complete":
            order.status = "completed"
        elif action == "cancel":
            order.status = "cancelled"

        if staff_id:
            try:
                staff = User.objects.get(id=staff_id)
                order.assigned_staff = staff
            except (User.DoesNotExist, ValueError):
                pass
        elif action == "luu_thay_doi":
            # Only clear staff if action is specifically to save changes and no staff was selected
            order.assigned_staff = None

        order.save()

        # Update or create InstallationTask only if an assignment exists
        if order.assigned_staff:
            from apps.tasks.models import InstallationTask
            task, created = InstallationTask.objects.get_or_create(order=order)
            task.assigned_staff = order.assigned_staff
            task.save()
        else:
            # If no staff is assigned, we should probably delete the task or clear its staff
            from apps.tasks.models import InstallationTask
            InstallationTask.objects.filter(order=order).update(assigned_staff=None)

        return order

    @staticmethod
    def calc_current_step(order):
        status_steps = ["pending", "confirmed", "processing", "completed"]
        if order.status in status_steps:
            return status_steps.index(order.status)
        return 0
