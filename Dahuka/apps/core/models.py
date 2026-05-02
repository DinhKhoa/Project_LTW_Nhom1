from django.db import models
from django.conf import settings
from apps.categories.models import Category
from apps.products.models import Product


class HomePageSettings(models.Model):
    # Banner
    banner_image = models.ImageField(
        upload_to="home/banners/", blank=True, null=True, verbose_name="Banner chính"
    )

    # Categories (Two Main)
    category_one = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="h_cat1",
        verbose_name="Danh mục nổi bật 1",
    )
    category_two = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="h_cat2",
        verbose_name="Danh mục nổi bật 2",
    )

    # Dahuka Pro Section
    dahuka_pro_title = models.CharField(
        max_length=255, default="Dahuka Hydrogen Pro", verbose_name="Tiêu đề Dahuka Pro"
    )
    dahuka_pro_desc = models.TextField(
        default="Dahuka Pro mới, với công nghệ Hydrogen Pro vượt trội...",
        verbose_name="Mô tả Dahuka Pro",
    )
    dahuka_pro_highlight = models.CharField(
        max_length=255,
        default="Uống nước mỗi ngày - Khoẻ vượt kỳ vọng",
        verbose_name="Điểm nhấn",
    )
    dahuka_pro_image = models.ImageField(
        upload_to="home/brands/", blank=True, null=True, verbose_name="Ảnh Dahuka Pro"
    )

    # Featured Products
    featured_products = models.ManyToManyField(
        Product, blank=True, verbose_name="Sản phẩm đặc sắc"
    )

    # Bottom CTA
    bottom_banner_image = models.ImageField(
        upload_to="home/banners/",
        blank=True,
        null=True,
        verbose_name="Banner chân trang",
    )
    bottom_cta_text = models.CharField(
        max_length=255,
        default="“Hãy đến và trải nghiệm sản phẩm Dahuka mới nhất...”",
        verbose_name="Thông điệp CTA",
    )

    class Meta:
        verbose_name = "Cài đặt Trang chủ"
        verbose_name_plural = "Cài đặt Trang chủ"

    def __str__(self):
        return "Cấu hình Trang chủ hiện tại"


class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="Người nhận",
    )
    title = models.CharField(max_length=255, verbose_name="Tiêu đề")
    message = models.TextField(verbose_name="Nội dung")
    link = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Đường dẫn"
    )
    is_read = models.BooleanField(default=False, verbose_name="Đã đọc")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    class Meta:
        verbose_name = "Thông báo"
        verbose_name_plural = "Các thông báo"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
