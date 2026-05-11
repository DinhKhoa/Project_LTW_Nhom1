from django.db.models import QuerySet, Q
from .models import Category

# ==============================================================================
# SELECTORS: TÁCH BIỆT LOGIC TRUY VẤN (Data Access Layer)
# ==============================================================================
# Theo quy tắc phát triển của dự án Dahuka, chúng ta không viết query trực tiếp
# (.filter, .exclude...) trong Views. Các hàm Selector này giúp quản lý tập trung
# các câu lệnh truy vấn để dễ dàng bảo trì và tái sử dụng ở nhiều nơi.

def get_category_queryset() -> QuerySet:
    """
    Lấy danh sách tất cả các danh mục sản phẩm hiện có trong hệ thống.
    Mặc định sắp xếp theo ID (Thứ tự từ cũ đến mới).
    
    Returns:
        QuerySet: Tập hợp các đối tượng Category.
    """
    return Category.objects.all().order_by("id")

def search_categories(query: str = "") -> QuerySet:
    """
    Hàm thực hiện tìm kiếm danh mục dựa trên từ khóa người dùng nhập vào.
    Hỗ trợ tìm kiếm thông minh theo cả Tên danh mục (name) và Đường dẫn (slug).
    
    Args:
        query (str): Từ khóa cần tìm kiếm.
    Returns:
        QuerySet: Danh sách các danh mục khớp với từ khóa.
    """
    # 1. Bắt đầu từ tập hợp QuerySet chuẩn (tất cả danh mục)
    qs = get_category_queryset()
    
    if query:
        # 2. Sử dụng đối tượng Q để thực hiện phép toán 'HOẶC' (OR) trong câu lệnh SQL
        # icontains: Tìm kiếm chứa chuỗi (không phân biệt chữ hoa hay chữ thường)
        qs = qs.filter(
            Q(name__icontains=query) | Q(slug__icontains=query)
        )
    return qs

def get_category_by_id(pk: int) -> Category:
    """
    Lấy thông tin chi tiết của một danh mục dựa trên Khóa chính (ID).
    
    Args:
        pk (int): Primary Key của danh mục cần tìm.
    Returns:
        Category: Đối tượng danh mục được tìm thấy.
    Throws:
        Http404: Tự động trả về trang lỗi 404 nếu không tìm thấy ID tương ứng.
    """
    from django.shortcuts import get_object_or_404
    return get_object_or_404(Category, pk=pk)
