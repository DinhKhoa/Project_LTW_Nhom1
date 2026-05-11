from typing import Any, Optional
from django.db.models import QuerySet
from .models import Customer, Address

# Selectors: Chứa các hàm truy vấn DB cho app account
# Views gọi các hàm này thay vì viết query trực tiếp

def get_customer_for_user(user: Any) -> Optional[Customer]:
    """Lấy Customer profile của user hiện tại; None nếu chưa đăng nhập."""
    if not user.is_authenticated:
        return None
    return Customer.objects.filter(user=user).first()

def get_addresses_for_customer(customer: Customer) -> QuerySet[Address]:
    """Lấy danh sách địa chỉ của khách hàng, địa chỉ mặc định hiển thị trước."""
    return Address.objects.filter(customer=customer).order_by('-is_default', '-updated_at')

def get_address_by_id(customer: Customer, address_id: int) -> Address:
    """Lấy 1 địa chỉ của khách hàng theo ID; 404 nếu không phải của họ."""
    from django.shortcuts import get_object_or_404
    return get_object_or_404(Address, id=address_id, customer=customer)

def get_filtered_purchases(user: Any, query: str = "", status: str = "") -> QuerySet:
    """Lấy đơn hàng của khách hàng, có thể lọc theo từ khóa và trạng thái."""
    from django.db.models import Q
    from apps.orders.models import Order
    
    # Chỉ lấy đơn của user đang đăng nhập, kèm thông tin nhân viên phụ trách
    orders = Order.objects.filter(customer=user).select_related(
        "customer", "assigned_staff"
    )

    if query:
        # Tìm theo tên, SĐT, tên sản phẩm, mã sản phẩm, hoặc mã số đơn
        search_filter = (
            Q(full_name__icontains=query)
            | Q(phone__icontains=query)
            | Q(items__product__name__icontains=query)
            | Q(items__product__id__icontains=query)
        )
        if query.isdigit():
            search_filter |= Q(id=query)  # Tìm theo mã đơn nếu nhập số
        orders = orders.filter(search_filter).distinct()

    if status:
        orders = orders.filter(status=status)

    return orders.order_by("-created_at")  # Đơn mới nhất lên đầu
