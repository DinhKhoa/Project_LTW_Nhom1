from django.db import models
from apps.products.models import Product

class Promotion(models.Model):
    TYPE_CHOICES = [
        ('percent', 'Phần trăm'),
        ('fixed', 'Giá cố định'),
    ]
    
    name = models.CharField(max_length=255, verbose_name='Tên khuyến mãi')
    code = models.CharField(max_length=50, unique=True, verbose_name='Mã khuyến mãi')
    condition = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name='Điều kiện áp dụng (Giá tối thiểu)')
    discount_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='percent', verbose_name='Hình thức')
    value = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Giá trị')
    
    start_date = models.DateField(verbose_name='Ngày bắt đầu')
    end_date = models.DateField(verbose_name='Ngày kết thúc')
    
    products = models.ManyToManyField(Product, blank=True, verbose_name='Sản phẩm áp dụng')
    is_active = models.BooleanField(default=True, verbose_name='Trạng thái')
    notification_sent = models.BooleanField(default=False, verbose_name='Đã gửi thông báo')

    class Meta:
        verbose_name = 'Khuyến mãi'
        verbose_name_plural = 'Quản lý khuyến mãi'

    def __str__(self):
        return self.name

    @property
    def is_currently_valid(self):
        from django.utils import timezone
        today = timezone.localtime().date()
        return self.is_active and self.start_date <= today <= self.end_date

    @property
    def status_display(self):
        from django.utils import timezone
        today = timezone.localtime().date()
        
        if self.start_date > today:
            return "Sắp diễn ra"
        
        if self.is_active and self.start_date <= today <= self.end_date:
            return "Đang hoạt động"
            
        return "Đã kết thúc"

    def calculate_discount(self, total_amount):
        if not self.is_currently_valid or total_amount < self.condition:
            return 0
            
        if self.discount_type == 'percent':
            discount = (self.value / 100) * total_amount
            return min(discount, total_amount) # Max discount is the total amount
        return min(self.value, total_amount)
