from django.contrib.auth import update_session_auth_hash
from django.shortcuts import get_object_or_404
from .models import Customer, Address

class AccountService:
    @staticmethod
    def get_or_create_customer(user):
        customer, created = Customer.objects.get_or_create(user=user)
        return customer

    @staticmethod
    def create_address(customer, data):
        if data.get('is_default'):
            Address.objects.filter(customer=customer).update(is_default=False)
        elif not Address.objects.filter(customer=customer).exists():
            data['is_default'] = True
            
        address = Address.objects.create(customer=customer, **data)
        return address

    @staticmethod
    def update_address(customer, address_id, data):
        address = get_object_or_404(Address, id=address_id, customer=customer)
        if data.get('is_default'):
            Address.objects.filter(customer=customer).exclude(id=address.id).update(is_default=False)
        
        for key, value in data.items():
            setattr(address, key, value)
        address.save()
        return address

    @staticmethod
    def delete_address(customer, address_id):
        address = get_object_or_404(Address, id=address_id, customer=customer)
        address.delete()
        return True

    @staticmethod
    def change_password(request, user, old_password, new_password):
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            return True, "Đổi mật khẩu thành công"
        return False, "Mật khẩu cũ không chính xác"

    @staticmethod
    def cancel_order(order, reason, user=None):
        from apps.orders.services import OrderService
        if order.status in ['pending', 'processing']:
            OrderService.handle_order_action(order, 'cancel', cancel_reason=reason, user=user)
            return True, "Đã hủy đơn hàng thành công"
        return False, "Không thể hủy đơn hàng này"

    @staticmethod
    def register_user(form_data: dict) -> bool:
        from django.contrib.auth.models import User
        user = User.objects.create_user(
            username=form_data["phone"],
            password=form_data["password"],
            email=form_data.get("email", ""),
            first_name=form_data["first_name"],
            last_name=form_data["last_name"],
        )

        birthday = form_data.get("birthday")
        if birthday:
            customer = user.customer
            customer.birthday = birthday
            customer.save()
        return True
