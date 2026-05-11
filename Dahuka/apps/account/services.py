from django.contrib.auth import update_session_auth_hash
from django.shortcuts import get_object_or_404
from .models import Customer, Address

# Service layer: Chứa toàn bộ business logic liên quan đến tài khoản
# Views chỉ gọi các hàm ở đây, không xử lý logic trực tiếp
class AccountService:

    # Lấy Customer đi kèm với User (tạo mới nếu chưa có)
    @staticmethod
    def get_or_create_customer(user):
        customer, created = Customer.objects.get_or_create(user=user)
        return customer

    # Tạo địa chỉ mới cho khách hàng
    # Nếu đánh dấu mặc định → bỏ mặc định của tất cả địa chỉ cũ
    @staticmethod
    def create_address(customer, cleaned_data):
        allowed_fields = ['full_name', 'phone', 'province', 'district', 'ward', 'address_detail', 'address_type', 'is_default']
        data = {k: v for k, v in cleaned_data.items() if k in allowed_fields}
        
        if data.get('is_default'):
            Address.objects.filter(customer=customer).update(is_default=False)
        elif not Address.objects.filter(customer=customer).exists():
            data['is_default'] = True
            
        address = Address.objects.create(customer=customer, **data)
        return address

    # Cập nhật địa chỉ đã có
    @staticmethod
    def update_address(customer, address_id, cleaned_data):
        address = get_object_or_404(Address, id=address_id, customer=customer)
        
        allowed_fields = ['full_name', 'phone', 'province', 'district', 'ward', 'address_detail', 'address_type', 'is_default']
        data = {k: v for k, v in cleaned_data.items() if k in allowed_fields}
        
        if data.get('is_default'):
            Address.objects.filter(customer=customer).exclude(id=address.id).update(is_default=False)
        
        for key, value in data.items():
            setattr(address, key, value)
        address.save()
        return address

    # Xóa địa chỉ của khách hàng
    @staticmethod
    def delete_address(customer, address_id):
        address = get_object_or_404(Address, id=address_id, customer=customer)
        address.delete()
        return True

    # Đổi mật khẩu khi đã đăng nhập (yêu cầu mật khẩu cũ)
    # update_session_auth_hash giữ phiên đăng nhập sau khi đổi MK
    @staticmethod
    def change_password(request, user, old_password, new_password):
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  # Giữ session, không bị đăng xuất
            return True, "Đổi mật khẩu thành công"
        return False, "Mật khẩu cũ không chính xác"

    # Hủy đơn hàng: chỉ hủy được khi đơn đang ở trạng thái chờ hoặc đang giao
    @staticmethod
    def cancel_order(order, reason, user=None):
        from apps.orders.services import OrderService
        if order.status in ['pending', 'processing']:
            OrderService.handle_order_action(order, 'cancel', cancel_reason=reason, user=user)
            return True, "Đã hủy đơn hàng thành công"
        return False, "Không thể hủy đơn hàng này"

    # Tạo tài khoản User mới từ dữ liệu form đăng ký
    # username = số điện thoại (dùng để đăng nhập)
    # Signal trong signals.py sẽ tự động tạo Customer sau khi User được tạo
    @staticmethod
    def register_user(form_data: dict) -> bool:
        from django.contrib.auth.models import User
        user = User.objects.create_user(
            username=form_data["phone"],       # SĐT là username đăng nhập
            password=form_data["password"],
            email=form_data.get("email", ""),
            first_name=form_data["first_name"],
            last_name=form_data["last_name"],
        )

        # Lưu ngày sinh vào Customer profile nếu có nhập
        birthday = form_data.get("birthday")
        if birthday:
            customer = user.customer
            customer.birthday = birthday
            customer.save()
        return True
