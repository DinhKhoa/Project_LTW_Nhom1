from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên danh mục")
    slug = models.SlugField(unique=True, blank=True)
    code = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="Mã danh mục")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name="Ảnh biểu tượng")
    banner_image = models.ImageField(upload_to='categories/banners/', blank=True, null=True, verbose_name="Ảnh banner")
    
    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục sản phẩm"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def ma_danh_muc(self):
        return self.code or str(self.id)

    @property
    def ten_danh_muc(self):
        return self.name
