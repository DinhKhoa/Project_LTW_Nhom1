from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    GENDER_CHOICES = (
        ("male", "Nam"),
        ("female", "Nữ"),
        ("other", "Khác"),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Số điện thoại")
    gender = models.CharField(
        max_length=10, choices=GENDER_CHOICES, default="male", verbose_name="Giới tính"
    )
    birthday = models.DateField(null=True, blank=True, verbose_name="Ngày sinh")
    rank = models.CharField(
        max_length=50, default="Classic", verbose_name="Hạng thành viên"
    )
    points = models.IntegerField(default=0, verbose_name="Điểm tích lũy")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Khách hàng"
        verbose_name_plural = "Dữ liệu khách hàng"

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"


class Address(models.Model):
    ADDRESS_TYPE_CHOICES = (
        ("home", "Nhà riêng/Chung cư"),
        ("office", "Văn phòng"),
        ("other", "Khác"),
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="addresses",
        verbose_name="Khách hàng",
    )
    full_name = models.CharField(max_length=100, verbose_name="Tên người nhận")
    phone = models.CharField(max_length=20, verbose_name="Số điện thoại")
    province = models.CharField(max_length=100, verbose_name="Tỉnh/Thành phố")
    district = models.CharField(max_length=100, verbose_name="Quận/Huyện")
    ward = models.CharField(max_length=100, verbose_name="Phường/Xã")
    address_detail = models.CharField(max_length=255, verbose_name="Địa chỉ chi tiết")
    address_type = models.CharField(
        max_length=20,
        choices=ADDRESS_TYPE_CHOICES,
        default="home",
        verbose_name="Loại địa chỉ",
    )
    is_default = models.BooleanField(default=False, verbose_name="Địa chỉ mặc định")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_default", "-updated_at"]
        verbose_name = "Địa chỉ"
        verbose_name_plural = "Số địa chỉ"

    def __str__(self):
        return f"{self.full_name} - {self.address_detail}"
