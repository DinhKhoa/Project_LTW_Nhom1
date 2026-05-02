from django.db import models
from apps.categories.models import Category

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Danh mục")
    name = models.CharField(max_length=255, verbose_name="Tên sản phẩm")
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(verbose_name="Mô tả chi tiết")
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Giá bán")
    image = models.ImageField(upload_to='products/', verbose_name="Hình ảnh chính", blank=True, null=True)
    image_specs = models.ImageField(upload_to='products/specs/', verbose_name="Ảnh thông số", blank=True, null=True)
    image_features = models.ImageField(upload_to='products/features/', verbose_name="Ảnh tính năng", blank=True, null=True)
    image_description = models.ImageField(upload_to='products/description/', verbose_name="Ảnh mô tả chi tiết", blank=True, null=True)
    stock = models.IntegerField(default=100, verbose_name="Tồn kho")
    
    # Specs
    short_description = models.TextField(blank=True, verbose_name="Mô tả ngắn")
    spec_power = models.CharField(max_length=100, blank=True, verbose_name="Công suất lọc")
    spec_technology = models.CharField(max_length=100, blank=True, verbose_name="Công nghệ lọc")
    spec_dimensions = models.CharField(max_length=100, blank=True, verbose_name="Kích thước")
    
    spec_type = models.CharField(max_length=100, blank=True, verbose_name="Loại máy")
    spec_capacity = models.CharField(max_length=100, blank=True, verbose_name="Dung tích bình")
    spec_hot_temp = models.CharField(max_length=100, blank=True, verbose_name="Nhiệt độ nóng")
    spec_cold_temp = models.CharField(max_length=100, blank=True, verbose_name="Nhiệt độ lạnh")
    spec_release_year = models.CharField(max_length=50, blank=True, verbose_name="Năm ra mắt")
    spec_origin = models.CharField(max_length=100, blank=True, verbose_name="Nơi sản xuất")
    spec_filters_count = models.CharField(max_length=50, blank=True, verbose_name="Số lõi lọc")
    spec_weight = models.CharField(max_length=50, blank=True, verbose_name="Khối lượng")
    spec_warranty = models.CharField(max_length=100, blank=True, verbose_name="Thời gian bảo hành")
    spec_water_source = models.CharField(max_length=100, blank=True, verbose_name="Loại nguồn nước")
    spec_features = models.TextField(blank=True, verbose_name="Tính năng")
    spec_other = models.TextField(blank=True, verbose_name="Thông số khác")

    is_active = models.BooleanField(default=True, verbose_name="Đang kinh doanh")
    is_featured = models.BooleanField(default=False, verbose_name="Nổi bật (Trang chủ)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Danh sách sản phẩm"

    def save(self, *args, **kwargs):
        # Auto disable featured if product is hidden
        if not self.is_active:
            self.is_featured = False

        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.name)
            self.slug = base_slug
            counter = 1
            # Ensure slug uniqueness by appending counter if collision detected
            while Product.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def main_image_url(self):
        if self.image:
            return self.image.url
        first_img = self.images.first()
        if first_img and first_img.image_url:
            return first_img.image_url.url
        return '/static/img/no-image.png'

    @property
    def stock_status(self):
        if self.stock <= 0:
            return 'het_hang'
        elif self.stock <= 10:
            return 'thap'
        return 'day_du'

    @property
    def stock_status_display(self):
        status = self.stock_status
        if status == 'het_hang':
            return 'Hết hàng'
        elif status == 'thap':
            return 'Sắp hết'
        return 'Đầy đủ'

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="Sản phẩm")
    image_url = models.ImageField(upload_to='products/gallery/', verbose_name="Hình ảnh", blank=True, null=True)
    caption = models.CharField(max_length=255, blank=True, verbose_name="Chú thích")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Hình ảnh chi tiết"
        verbose_name_plural = "Thư viện ảnh sản phẩm"
