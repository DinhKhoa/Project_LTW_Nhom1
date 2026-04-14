from django.db import models
from apps.categories.models import Category

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Danh mục")
    name = models.CharField(max_length=255, verbose_name="Tên sản phẩm")
    slug = models.SlugField(unique=True, blank=True)
    sku = models.CharField(max_length=50, unique=True, verbose_name="Mã SKU")
    description = models.TextField(verbose_name="Mô tả chi tiết")
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Giá bán")
    image = models.ImageField(upload_to='products/', verbose_name="Hình ảnh chính")
    stock = models.IntegerField(default=100, verbose_name="Tồn kho")
    
    # Specs
    spec_power = models.CharField(max_length=100, blank=True, verbose_name="Công suất lọc")
    spec_technology = models.CharField(max_length=100, blank=True, verbose_name="Công nghệ lọc")
    spec_dimensions = models.CharField(max_length=100, blank=True, verbose_name="Kích thước")
    
    is_active = models.BooleanField(default=True, verbose_name="Đang kinh doanh")
    is_featured = models.BooleanField(default=False, verbose_name="Nổi bật (Trang chủ)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Danh sách sản phẩm"

    def __str__(self):
        return self.name
