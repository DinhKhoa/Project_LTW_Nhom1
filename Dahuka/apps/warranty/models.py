from django.db import models

class WarrantyPageSettings(models.Model):
    title = models.CharField(max_length=255, default='Điểm bán - Bảo hành', verbose_name="Tiêu đề trang")
    
    # Hai ảnh cần chỉnh sửa
    image_one = models.ImageField(upload_to='warranty/', blank=True, null=True, verbose_name="Ảnh minh họa 1")
    image_two = models.ImageField(upload_to='warranty/', blank=True, null=True, verbose_name="Ảnh minh họa 2")
    
    # Các thông tin khác nếu cần
    store_location_title = models.CharField(max_length=255, default='Vị trí cửa hàng', verbose_name="Tiêu đề Vị trí")
    online_contact_title = models.CharField(max_length=255, default='Liên hệ trực tuyến', verbose_name="Tiêu đề Liên hệ")

    class Meta:
        verbose_name = "Cài đặt Trang Bảo hành"
        verbose_name_plural = "Cài đặt Trang Bảo hành"

    def __str__(self):
        return "Cấu hình Trang Bảo hành"
