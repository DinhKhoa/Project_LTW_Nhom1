from django.contrib import admin
from .models import Product

# Đăng ký model Product vào trang quản trị Django Admin
# Admin vào /admin/products/product/ để quản lý sản phẩm
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Các cột hiển thị trong bảng danh sách sản phẩm
    list_display = ('name', 'price', 'stock', 'category', 'is_active', 'is_featured')
    # Bộ lọc bên phải màn hình: lọc theo danh mục, trạng thái kinh doanh, nổi bật
    list_filter = ('category', 'is_active', 'is_featured')
    # Thanh tìm kiếm: tìm theo tên sản phẩm
    search_fields = ('name',)
    # Tự động điền slug từ tên sản phẩm khi admin gõ
    prepopulated_fields = {'slug': ('name',)}
