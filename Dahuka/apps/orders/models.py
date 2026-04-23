from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('confirmed', 'Đã xác nhận'),
        ('processing', 'Đang xử lý/Giao hàng'),
        ('completed', 'Đã hoàn thành'),
        ('cancelled', 'Đã hủy'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name="Khách hàng")
    full_name = models.CharField(max_length=100, verbose_name="Họ tên người nhận")
    phone = models.CharField(max_length=15, verbose_name="Số điện thoại")
    city = models.CharField(max_length=100, verbose_name="Tỉnh/Thành phố", blank=True)
    district = models.CharField(max_length=100, verbose_name="Quận/Huyện", blank=True)
    ward = models.CharField(max_length=100, verbose_name="Phường/Xã", blank=True)
    house_details = models.CharField(max_length=255, verbose_name="Số nhà, tên đường", blank=True)
    
    total_amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Tổng tiền")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Trạng thái")
    
    PAYMENT_METHOD_CHOICES = [
        ('tien_mat', 'Tiền mặt'),
        ('chuyen_khoan', 'Chuyển khoản'),
    ]
    hinh_thuc_thanh_toan = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='chuyen_khoan', verbose_name="Hình thức thanh toán")
    
    PAYMENT_STATUS_CHOICES = [
        ('chua_thanh_toan', 'Chưa thanh toán'),
        ('da_thanh_toan', 'Đã thanh toán'),
    ]
    trang_thai_thanh_toan = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='chua_thanh_toan', verbose_name="Trạng thái thanh toán")
    
    assigned_staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_orders', verbose_name="Nhân viên phụ trách")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đặt")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Quản lý đơn hàng"

    @property
    def full_address(self):
        parts = [self.house_details, self.ward, self.district, self.city]
        return ", ".join([p for p in parts if p])

    def __str__(self):
        return f"Order #{self.id} - {self.full_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Đơn hàng")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name="Sản phẩm")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Số lượng")
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Đơn giá")

    def __str__(self):
        return f"{self.product.name if self.product else 'N/A'} (x{self.quantity})"
