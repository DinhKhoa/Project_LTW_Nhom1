from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product

class WarrantyCard(models.Model):
    serial_number = models.CharField(max_length=100, unique=True, verbose_name="Số Serial")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Sản phẩm")
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Khách hàng")
    
    activated_date = models.DateField(null=True, blank=True, verbose_name="Ngày kích hoạt")
    expiry_date = models.DateField(null=True, blank=True, verbose_name="Ngày hết hạn")
    is_active = models.BooleanField(default=False, verbose_name="Trạng thái kích hoạt")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Thẻ bảo hành"
        verbose_name_plural = "Quản lý bảo hành"

    def __str__(self):
        return f"{self.serial_number} - {self.product.name}"

class MaintenanceHistory(models.Model):
    warranty_card = models.ForeignKey(WarrantyCard, on_delete=models.CASCADE, related_name='maintenance_logs', verbose_name="Thẻ bảo hành")
    date = models.DateField(verbose_name="Ngày bảo trì")
    work_done = models.TextField(verbose_name="Nội dung thực hiện")
    technician = models.CharField(max_length=255, verbose_name="Kỹ thuật viên")
    next_maintenance_date = models.DateField(null=True, blank=True, verbose_name="Hẹn bảo trì tiếp theo")

    class Meta:
        verbose_name = "Lịch sử bảo trì"
        verbose_name_plural = "Lịch sử bảo trì"

    def __str__(self):
        return f"Log for {self.warranty_card.serial_number} on {self.date}"
