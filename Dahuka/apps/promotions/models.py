from django.db import models
from apps.products.models import Product

class Promotion(models.Model):
    TYPE_CHOICES = [
        ('percent', 'Phần trăm'),
        ('fixed', 'Giá cố định'),
    ]
    
    name = models.CharField(max_length=255, verbose_name='Tên khuyến mãi')
    code = models.CharField(max_length=50, unique=True, verbose_name='Mã khuyến mãi')
    condition = models.TextField(blank=True, verbose_name='Điều kiện áp dụng')
    discount_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='percent', verbose_name='Hình thức')
    value = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Giá trị')
    
    start_date = models.DateField(verbose_name='Ngày bắt đầu')
    end_date = models.DateField(verbose_name='Ngày kết thúc')
    
    products = models.ManyToManyField(Product, blank=True, verbose_name='Sản phẩm áp dụng')
    is_active = models.BooleanField(default=True, verbose_name='Trạng thái')

    class Meta:
        verbose_name = 'Khuyến mãi'
        verbose_name_plural = 'Quản lý khuyến mãi'

    def __str__(self):
        return self.name

    @property
    def status_display(self):
        from django.utils import timezone
        today = timezone.now().date()
        if not self.is_active or self.end_date < today:
            return "Đã kết thúc"
        elif self.start_date > today:
            return "Sắp diễn ra"
        else:
            return "Đang hoạt động"
