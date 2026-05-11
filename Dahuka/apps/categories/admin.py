from django.contrib import admin
from .models import Category


# ==============================================================================
# CẤU HÌNH GIAO DIỆN QUẢN TRỊ (Django Admin)
# ==============================================================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Tùy chỉnh cách hiển thị và quản lý Danh mục sản phẩm trong trang Admin.
    Giúp người quản trị dễ dàng thao tác với dữ liệu danh mục.
    """

    # 1. Định nghĩa các cột sẽ hiển thị trong bảng danh sách danh mục
    # 'name': Hiển thị tên, 'slug': Hiển thị đường dẫn URL thân thiện
    list_display = ("name", "slug")

    # 2. Cấu hình tính năng tìm kiếm (Thanh tìm kiếm sẽ xuất hiện ở đầu bảng)
    # Cho phép tìm nhanh danh mục theo tên hoặc theo slug
    search_fields = ("name", "slug")

    # 3. Tính năng Tự động điền (Prepopulated):
    # Khi Admin gõ tên vào ô 'name', hệ thống Javascript của Admin sẽ tự động
    # tạo và điền giá trị tương ứng vào ô 'slug' ngay lập tức.
    prepopulated_fields = {"slug": ("name",)}

    # Có thể thêm các cấu hình khác như:
    # list_per_page = 20  # Phân trang, hiển thị 20 danh mục trên một trang
