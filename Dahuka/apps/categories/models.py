from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên danh mục")
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Mô tả")
    image = models.ImageField(
        upload_to="categories/", blank=True, null=True, verbose_name="Ảnh biểu tượng"
    )
    banner_image = models.ImageField(
        upload_to="categories/banners/",
        blank=True,
        null=True,
        verbose_name="Ảnh banner",
    )

    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục sản phẩm"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = base_slug
            counter = 1
            while Category.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
