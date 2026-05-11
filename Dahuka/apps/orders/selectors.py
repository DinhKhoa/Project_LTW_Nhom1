from typing import Optional
from django.core.paginator import Page, Paginator
from django.db.models import Q, QuerySet
from django.contrib.auth.models import User
from apps.core.constants import DEFAULT_PAGE_SIZE
from .models import Order

# ==============================================================================
# SELECTORS: CHUYÊN TRUY VẤN DỮ LIỆU ĐƠN HÀNG (READ-ONLY)
# ==============================================================================

def get_orders_queryset(
    query: str = "", status_filter: str = "", user: Optional[User] = None
) -> QuerySet[Order]:
    """
    Lấy danh sách đơn hàng có lọc theo từ khóa và trạng thái.
    Áp dụng logic phân quyền: Khách thường chỉ thấy đơn của họ, Admin thấy hết.
    """
    orders = Order.objects.all()

    # Phân quyền: Nếu không phải nhân viên (is_staff=False), chỉ lọc đơn của chính user đó
    if user and not user.is_staff:
        orders = orders.filter(customer=user)

    # Lọc theo từ khóa (Mã đơn, Tên khách hoặc SĐT) sử dụng Q Object (OR)
    if query:
        orders = orders.filter(
            Q(order_code__icontains=query)
            | Q(full_name__icontains=query)
            | Q(phone__icontains=query)
        )

    # Lọc theo trạng thái đơn hàng (pending, processing, v.v.)
    if status_filter:
        orders = orders.filter(status=status_filter)

    # TỐI ƯU HÓA: prefetch_related giúp tải trước toàn bộ sản phẩm (items) trong đơn
    # giúp tránh tình trạng gửi hàng trăm câu lệnh SQL khi lặp qua danh sách đơn hàng.
    return orders.prefetch_related("items__product").order_by("-created_at", "-id")


def get_paginated_orders(
    query: str = "",
    status_filter: str = "",
    page_number: int = 1,
    per_page: Optional[int] = None,
    user: Optional[User] = None,
) -> Page:
    """
    Kết hợp việc lấy dữ liệu (queryset) và chia trang (pagination).
    Trả về một 'Page' object chứa danh sách đơn hàng của trang hiện tại.
    """
    if per_page is None:
        per_page = DEFAULT_PAGE_SIZE

    # 1. Lấy toàn bộ danh sách đã lọc
    orders = get_orders_queryset(query, status_filter, user)
    
    # 2. Khởi tạo bộ chia trang (Paginator)
    paginator = Paginator(orders, per_page)
    
    # 3. Trả về đúng trang người dùng đang đứng (VD: trang 2)
    return paginator.get_page(page_number)


def get_order_statistics() -> dict:
    """
    Tính toán số liệu thống kê nhanh cho trang quản trị.
    Trả về Dictionary chứa số lượng đơn theo từng trạng thái.
    Dùng để hiển thị các con số trên Top Bar của trang danh sách đơn hàng.
    """
    return {
        "total": Order.objects.count(),
        "pending": Order.objects.filter(status="pending").count(),
        "confirmed": Order.objects.filter(status="confirmed").count(),
        "processing": Order.objects.filter(status="processing").count(),
        "completed": Order.objects.filter(status="completed").count(),
        "cancelled": Order.objects.filter(status="cancelled").count(),
    }


def get_order_detail(pk: int) -> Order:
    """
    Lấy thông tin CHI TIẾT của 1 đơn hàng cụ thể.
    Sử dụng các kỹ thuật JOIN bảng nâng cao để tăng tốc độ load trang.
    """
    from django.db.models import Prefetch
    from .models import OrderItem

    # 1. select_related: Dùng cho ForeignKey (JOIN bảng ngay trong SQL)
    # Ở đây join bảng Product vào bảng OrderItem luôn.
    items_qs = OrderItem.objects.select_related("product").all()
    
    # 2. Truy vấn chính:
    # - join với bảng User (Customer & Staff)
    # - Tải trước tập hợp items (đã được join product ở trên)
    return (
        Order.objects.select_related("customer", "assigned_staff")
        .prefetch_related(Prefetch("items", queryset=items_qs))
        .get(pk=pk)
    )
