from typing import Optional
from django.db.models import QuerySet, Q
from .models import Product

# Selectors: Chứa các hàm truy vấn DB cho app products
# Views gọi các hàm này thay vì viết query trực tiếp


def get_filtered_products(
    query: str = "",
    category_id: str = "all",
    inventory_filter: str = "default",
    is_active: Optional[bool] = None,
) -> QuerySet[Product]:
    """Lọc sản phẩm theo từ khóa, danh mục và sắp xếp theo tồn kho."""
    # select_related: Kỹ thuật JOIN trong SQL giúp lấy thông tin Danh mục ngay lập tức.
    # Tránh lỗi N+1 query (mỗi sản phẩm lại tốn thêm 1 câu lệnh để lấy tên danh mục).
    products = Product.objects.select_related("category").all()

    if is_active is not None:
        products = products.filter(is_active=is_active)

    if query:
        # Q(name__icontains=query):
        # - icontains: Tìm kiếm chuỗi con, KHÔNG phân biệt hoa thường.
        # - Q: Dùng để thực hiện các câu lệnh lọc phức tạp.
        products = products.filter(Q(name__icontains=query))

    if category_id != "all":
        products = products.filter(category_id=category_id)  # Lọc theo danh mục

    # Sắp xếp theo tồn kho nếu admin chọn
    if inventory_filter == "low-to-high":
        products = products.order_by("stock")  # Tồn kho tăng dần
    elif inventory_filter == "high-to-low":
        products = products.order_by("-stock")  # Tồn kho giảm dần
    else:
        products = products.order_by("-id")  # Mặc định: mới nhất trước

    return products


def get_product_by_id(pk: int) -> Product:
    """Lấy 1 sản phẩm theo ID kèm thông tin danh mục; 404 nếu không tìm thấy."""
    from django.shortcuts import get_object_or_404

    return get_object_or_404(Product.objects.select_related("category"), pk=pk)
