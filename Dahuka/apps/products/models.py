from django.db import models
from apps.categories.models import Category

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Danh mục")
    name = models.CharField(max_length=255, verbose_name="Tên sản phẩm")
    slug = models.SlugField(unique=True, blank=True)
    sku = models.CharField(max_length=50, unique=True, verbose_name="Mã SKU")
    description = models.TextField(verbose_name="Mô tả chi tiết")
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Giá bán")
    image = models.ImageField(upload_to='products/', verbose_name="Hình ảnh chính", blank=True, null=True)
    stock = models.IntegerField(default=100, verbose_name="Tồn kho")
    
    # Specs
    short_description = models.TextField(blank=True, verbose_name="Mô tả ngắn")
    spec_power = models.CharField(max_length=100, blank=True, verbose_name="Công suất lọc")
    spec_technology = models.CharField(max_length=100, blank=True, verbose_name="Công nghệ lọc")
    spec_dimensions = models.CharField(max_length=100, blank=True, verbose_name="Kích thước")
    
    spec_loai_may = models.CharField(max_length=100, blank=True, verbose_name="Loại máy")
    spec_dung_tich = models.CharField(max_length=100, blank=True, verbose_name="Dung tích bình")
    spec_nhiet_do_nong = models.CharField(max_length=100, blank=True, verbose_name="Nhiệt độ nóng")
    spec_nhiet_do_lanh = models.CharField(max_length=100, blank=True, verbose_name="Nhiệt độ lạnh")
    spec_nam_ra_mat = models.CharField(max_length=50, blank=True, verbose_name="Năm ra mắt")
    spec_noi_san_xuat = models.CharField(max_length=100, blank=True, verbose_name="Nơi sản xuất")
    spec_so_loi_loc = models.CharField(max_length=50, blank=True, verbose_name="Số lõi lọc")
    spec_khoi_luong = models.CharField(max_length=50, blank=True, verbose_name="Khối lượng")
    spec_bao_hanh = models.CharField(max_length=100, blank=True, verbose_name="Thời gian bảo hành")
    spec_nguon_nuoc = models.CharField(max_length=100, blank=True, verbose_name="Loại nguồn nước")
    spec_tinh_nang = models.TextField(blank=True, verbose_name="Tính năng")
    spec_thong_so_khac = models.TextField(blank=True, verbose_name="Thông số khác")

    is_active = models.BooleanField(default=True, verbose_name="Đang kinh doanh")
    is_featured = models.BooleanField(default=False, verbose_name="Nổi bật (Trang chủ)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Danh sách sản phẩm"

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def ma_san_pham(self):
        return self.sku

    @property
    def ten_san_pham(self):
        return self.name

    @property
    def gia_tien(self):
        return self.price

    @property
    def ton_kho(self):
        return self.stock

    @property
    def trang_thai_hien_thi(self):
        return self.is_active

    @property
    def danh_muc(self):
        return self.category

    @property
    def ten_danh_muc(self):
        return self.category.name if self.category else "Chưa phân loại"

    @property
    def ma_danh_muc(self):
        return self.category.code if self.category and self.category.code else (str(self.category.id) if self.category else "")

    @property
    def trang_thai_ton_kho(self):
        if self.stock == 0:
            return 'het_hang'
        elif self.stock < 10:
            return 'thap'
        return 'day_du'

    @property
    def trang_thai_ton_kho_display(self):
        if self.stock == 0:
            return 'Hết hàng'
        elif self.stock < 10:
            return 'Sắp hết'
        return 'Đầy đủ'

    @property
    def main_image_url(self):
        if self.image:
            return self.image.url
        first_img = self.images.first()
        if first_img:
            return first_img.image_url
        return '/static/img/no-image.png'

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="Sản phẩm")
    image_url = models.URLField(max_length=500, verbose_name="URL hình ảnh")
    caption = models.CharField(max_length=255, blank=True, verbose_name="Chú thích")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Hình ảnh chi tiết"
        verbose_name_plural = "Thư viện ảnh sản phẩm"
