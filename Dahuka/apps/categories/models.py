from django.db import models
from django.utils.text import slugify


# ==============================================================================
# MODEL: DANH MỤC SẢN PHẨM (Category)
# ==============================================================================
class Category(models.Model):
    """
    Model lưu trữ các nhóm sản phẩm (Ví dụ: Máy lọc nước RO, Cây nước nóng lạnh).
    Giúp phân loại sản phẩm để khách hàng dễ dàng tìm kiếm và lọc dữ liệu.
    """
    
    # Tên hiển thị của danh mục (VD: Máy lọc nước gia đình)
    name = models.CharField(max_length=100, verbose_name="Tên danh mục")
    
    # Đường dẫn URL thân thiện (VD: may-loc-nuoc-gia-dinh)
    # unique=True: Đảm bảo không có 2 danh mục trùng URL trong hệ thống
    slug = models.SlugField(unique=True, blank=True)
    
    # Mô tả ngắn gọn về đặc điểm của danh mục sản phẩm này
    description = models.TextField(blank=True, verbose_name="Mô tả")
    
    # Ảnh đại diện nhỏ cho danh mục (Thường hiển thị ở icon menu hoặc danh sách trang chủ)
    image = models.ImageField(
        upload_to="categories/", 
        blank=True, 
        null=True, 
        verbose_name="Ảnh biểu tượng"
    )
    
    # Ảnh lớn (Banner) hiển thị ở đầu trang khi khách hàng vào xem danh sách sản phẩm của danh mục
    banner_image = models.ImageField(
        upload_to="categories/banners/",
        blank=True,
        null=True,
        verbose_name="Ảnh banner",
    )

    class Meta:
        # Tên hiển thị trong giao diện quản trị Admin
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục sản phẩm"

    def save(self, *args, **kwargs):
        """
        Ghi đè phương thức save để tự động xử lý dữ liệu trước khi lưu vào Database.
        Cơ chế: Tự động tạo 'slug' từ 'name' nếu người dùng để trống.
        """
        # 1. Kiểm tra nếu chưa có slug, tiến hành tạo từ trường 'name' (sử dụng hàm slugify)
        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = base_slug
            counter = 1
            
            # 2. Vòng lặp kiểm tra trùng lặp: Nếu slug đã tồn tại ở danh mục khác
            # thì thêm số đếm vào cuối (Ví dụ: may-loc-nuoc -> may-loc-nuoc-1)
            while Category.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        
        # 3. Sau khi xử lý xong, gọi phương thức save gốc của Django để lưu vào database
        super().save(*args, **kwargs)

    def __str__(self):
        # Trả về tên danh mục khi hiển thị trong Admin hoặc các danh sách lựa chọn
        return self.name
