from django.contrib.auth import authenticate, update_session_auth_hash
from .models import Customer, Address
from apps.orders.models import Order

class AccountService:
    @staticmethod
    def get_or_create_customer(user):
        customer, created = Customer.objects.get_or_create(user=user)
        return customer

    @staticmethod
    def create_address(customer, form):
        address = form.save(commit=False)
        address.customer = customer
        if address.is_default:
            Address.objects.filter(customer=customer).update(is_default=False)
        address.save()
        return address

    @staticmethod
    def update_address(customer, address, form):
        address = form.save(commit=False)
        if address.is_default:
            Address.objects.filter(customer=customer).exclude(id=address.id).update(is_default=False)
        address.save()
        return address

    @staticmethod
    def change_password(request, user, old_password, new_password):
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user) # refresh session
            return True, "Đổi mật khẩu thành công"
        return False, "Mật khẩu cũ không chính xác"

    @staticmethod
    def cancel_order(order, reason):
        if order.status in ['pending', 'processing']:
            order.status = 'cancelled'
            order.save()
            return True, "Đã hủy đơn hàng thành công"
        return False, "Không thể hủy đơn hàng này"
