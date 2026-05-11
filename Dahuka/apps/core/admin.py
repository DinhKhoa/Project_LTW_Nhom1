from django.contrib import admin
from .models import HomePageSettings

# Cấu hình giao diện quản trị cho Cài đặt Trang chủ
@admin.register(HomePageSettings)
class HomePageSettingsAdmin(admin.ModelAdmin):
    """
    Giúp Admin có thể chỉnh sửa các thông tin như Banner, tiêu đề trang chủ
    ngay trong giao diện /admin/ của Django.
    """
    list_display = ("__str__",) # Hiển thị tên đại diện của bản ghi trong danh sách
