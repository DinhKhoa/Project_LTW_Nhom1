from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product
import random
import re
from django.utils import timezone
import datetime

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('confirmed', 'Đã xác nhận'),
        ('processing', 'Đang giao'),
        ('completed', 'Đã hoàn thành'),
        ('cancelled', 'Đã hủy'),
    ]
    
    order_code = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="Mã đơn hàng")
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name="Khách hàng", null=True, blank=True)
    full_name = models.CharField(max_length=100, verbose_name="Họ tên người nhận")
    phone = models.CharField(max_length=15, verbose_name="Số điện thoại")
    city = models.CharField(max_length=100, verbose_name="Tỉnh/Thành phố", blank=True)
    district = models.CharField(max_length=100, verbose_name="Quận/Huyện", blank=True)
    ward = models.CharField(max_length=100, verbose_name="Phường/Xã", blank=True)
    house_details = models.CharField(max_length=255, verbose_name="Số nhà, tên đường", blank=True)
    
    total_amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Tổng tiền")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Trạng thái")
    
    PAYMENT_METHOD_CHOICES = [
        ('full', 'Thanh toán toàn bộ'),
        ('deposit', 'Thanh toán cọc'),
    ]
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='full', verbose_name="Hình thức thanh toán")
    deposit_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Số tiền cọc")
    
    PAYMENT_STATUS_CHOICES = [
        ('chua_thanh_toan', 'Chưa thanh toán'),
        ('da_thanh_toan', 'Đã thanh toán'),
    ]
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='chua_thanh_toan', verbose_name="Trạng thái thanh toán")
    
    assigned_staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_orders', verbose_name="Nhân viên phụ trách")
    note = models.TextField(verbose_name="Ghi chú của khách hàng", blank=True, null=True)
    cancel_reason = models.TextField(verbose_name="Lý do hủy", blank=True, null=True)
    proof_image = models.ImageField(upload_to='order_proofs/', blank=True, null=True, verbose_name="Ảnh minh chứng")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đặt")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Quản lý đơn hàng"

    @property
    def full_address(self):
        parts = [self.house_details, self.ward, self.district, self.city]
        return ", ".join([p for p in parts if p])

    @property
    def remaining_amount(self):
        """Calculates the balance due for the order."""
        return self.total_amount - self.deposit_amount

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_status = None
        if not is_new:
            try:
                old_order = Order.objects.get(pk=self.pk)
                old_status = old_order.status
            except Order.DoesNotExist:
                pass
                
        if not self.order_code:
            date_str = timezone.localtime().strftime("%Y%m%d")
            rand_digits = "".join([str(random.randint(0, 9)) for _ in range(5)])
            self.order_code = f"DHK-{date_str}-{rand_digits}"
            while Order.objects.filter(order_code=self.order_code).exclude(pk=self.pk).exists():
                rand_digits = "".join([str(random.randint(0, 9)) for _ in range(5)])
                self.order_code = f"DHK-{date_str}-{rand_digits}"

        super().save(*args, **kwargs)

        # Tính toán warranty_expiration cho từng item nếu chuyển sang completed
        if not is_new and old_status != 'completed' and self.status == 'completed':
            items = self.items.all()
            total_items = items.count()
            for i, item in enumerate(items):
                if not item.warranty_expiration:
                    months = 24 # default 24 months
                    if item.product and item.product.spec_warranty:
                        warranty_str = item.product.spec_warranty.lower()
                        numbers = re.findall(r'\d+', warranty_str)
                        if numbers:
                            val = int(numbers[0])
                            if 'năm' in warranty_str or 'nam' in warranty_str:
                                val *= 12
                            months = val
                    
                    try:
                        current_time = timezone.localtime()
                        if months % 12 == 0:
                            years = months // 12
                            item.warranty_expiration = current_time.replace(year=current_time.year + years)
                        else:
                            item.warranty_expiration = current_time + datetime.timedelta(days=int(months * 30.44))
                    except Exception:
                        item.warranty_expiration = timezone.localtime() + datetime.timedelta(days=months * 30)
                    
                    item.save()

                    item.save()

    def __str__(self):
        return f"Order #{self.id} - {self.full_name} ({self.order_code})"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Đơn hàng")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name="Sản phẩm")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Số lượng")
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Đơn giá")
    warranty_expiration = models.DateTimeField(blank=True, null=True, verbose_name="Ngày hết hạn bảo hành")

    def __str__(self):
        return f"{self.product.name if self.product else 'N/A'} (x{self.quantity})"

    @property
    def get_total_price(self):
        return self.price * self.quantity
