from django.contrib import admin
from .models import DanhMuc, SanPham


@admin.register(DanhMuc)
class DanhMucAdmin(admin.ModelAdmin):
    list_display = ['ma_danh_muc', 'ten_danh_muc', 'so_luong_san_pham']
    search_fields = ['ma_danh_muc', 'ten_danh_muc']


@admin.register(SanPham)
class SanPhamAdmin(admin.ModelAdmin):
    list_display = ['ma_san_pham', 'ten_san_pham', 'gia_tien', 'ton_kho', 'trang_thai_hien_thi', 'danh_muc']
    search_fields = ['ma_san_pham', 'ten_san_pham']
    list_filter = ['danh_muc', 'trang_thai_hien_thi']
