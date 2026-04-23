from django.db import models
from django.contrib.auth.models import User
from apps.orders.models import Order

class InstallationTask(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chưa lắp đặt'),
        ('in_progress', 'Đang xử lý'),
        ('completed', 'Đã lắp đặt'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='installation_task', verbose_name="Đơn hàng")
    assigned_staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='installation_tasks', verbose_name='Nhân viên phụ trách')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Trạng thái")
    note = models.TextField(blank=True, verbose_name="Ghi chú")

    class Meta:
        verbose_name = 'Nhiệm vụ lắp đặt'
        verbose_name_plural = 'Quản lý lắp đặt'

    def __str__(self):
        staff = self.assigned_staff.get_full_name() if self.assigned_staff else 'Unassigned'
        return f"Task for Order #{self.order.id} - {staff}"
