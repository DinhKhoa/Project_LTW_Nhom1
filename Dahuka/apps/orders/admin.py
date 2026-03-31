from django.contrib import admin
from .models import DonDatHang, ChiTietDonHang


class ChiTietDonHangInline(admin.TabularInline):
    model = ChiTietDonHang
    extra = 1


@admin.register(DonDatHang)
class DonDatHangAdmin(admin.ModelAdmin):
    list_display = ['ma_don_hang', 'ho_ten', 'ngay_dat_don', 'trang_thai', 'tong_tien_hang']
    search_fields = ['ma_don_hang', 'ho_ten']
    list_filter = ['trang_thai', 'hinh_thuc_thanh_toan']
    inlines = [ChiTietDonHangInline]
