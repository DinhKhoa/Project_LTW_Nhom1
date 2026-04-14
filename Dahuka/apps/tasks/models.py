from django.db import models
from apps.orders.models import Order

class InstallationTask(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chưa lắp đặt'),
        ('in_progress', 'Đang xử lý'),
        ('completed', 'Đã lắp đặt'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='installation_task', verbose_name="Đơn hàng")
    staff_name = models.CharField(max_length=200, verbose_name='Nhân viên kỹ thuật')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Trạng thái")
    note = models.TextField(blank=True, verbose_name="Ghi chú")

    class Meta:
        verbose_name = 'Nhiệm vụ lắp đặt'
        verbose_name_plural = 'Quản lý lắp đặt'

    def __str__(self):
        return f"Task for Order #{self.order.id}"
