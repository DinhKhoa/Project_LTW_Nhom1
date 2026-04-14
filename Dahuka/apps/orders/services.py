from django.core.paginator import Paginator
from django.db.models import Q
from .models import Order, OrderItem
from django.contrib.auth.models import User

class OrderService:
    @staticmethod
    def create_order(customer, full_name, phone, address, cart_items):
        total_amount = sum(item['price'] * item.get('quantity', 1) for item in cart_items)
        
        order = Order.objects.create(
            customer=customer,
            full_name=full_name,
            phone=phone,
            address=address,
            total_amount=total_amount,
            status='pending'
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product_id=item['product_id'],
                quantity=item.get('quantity', 1),
                price=item['price']
            )
        
        return order

    @staticmethod
    def get_orders(query='', status_filter='', page_number=1, per_page=10):
        orders = Order.objects.all()

        if query:
            orders = orders.filter(
                Q(id__icontains=query) | Q(full_name__icontains=query) | Q(phone__icontains=query)
            )

        if status_filter:
            orders = orders.filter(status=status_filter)

        orders = orders.order_by('-created_at')
        paginator = Paginator(orders, per_page)
        return paginator.get_page(page_number)

    @staticmethod
    def handle_order_action(order, action, staff_id=''):
        if action == 'confirm':
            order.status = 'confirmed'
        elif action == 'start_shipping':
            order.status = 'processing'
        elif action == 'complete':
            order.status = 'completed'
        elif action == 'cancel':
            order.status = 'cancelled'
        
        if staff_id:
            try:
                staff = User.objects.get(id=staff_id)
                order.assigned_staff = staff
            except User.DoesNotExist:
                pass
        
        order.save()
        return order

    @staticmethod
    def calc_current_step(order):
        status_steps = ['pending', 'confirmed', 'processing', 'completed']
        if order.status in status_steps:
            return status_steps.index(order.status)
        return 0
