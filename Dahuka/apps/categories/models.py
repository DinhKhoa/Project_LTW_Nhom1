from django.db import models


class DanhMuc(models.Model):
    ma_danh_muc = models.CharField(max_length=20, unique=True, verbose_name='Mã danh mục')
    ten_danh_muc = models.CharField(max_length=200, verbose_name='Tên danh mục')

    class Meta:
        verbose_name = 'Danh mục'
        verbose_name_plural = 'Danh mục'
        ordering = ['ma_danh_muc']

    def __str__(self):
        return f"{self.ma_danh_muc} - {self.ten_danh_muc}"

    @property
    def so_luong_san_pham(self):
        return self.sanpham_set.count()


class SanPham(models.Model):
    TRANG_THAI_TON_KHO = [
        ('day_du', 'Đầy đủ'),
        ('thap', 'Thấp'),
        ('het_hang', 'Hết hàng'),
    ]

    ma_san_pham = models.CharField(max_length=20, unique=True, verbose_name='Mã sản phẩm')
    ten_san_pham = models.CharField(max_length=300, verbose_name='Tên sản phẩm')
    gia_tien = models.DecimalField(max_digits=15, decimal_places=0, verbose_name='Giá tiền')
    ton_kho = models.IntegerField(default=0, verbose_name='Tồn kho')
    trang_thai_hien_thi = models.BooleanField(default=True, verbose_name='Trạng thái hiển thị')
    danh_muc = models.ForeignKey(DanhMuc, on_delete=models.CASCADE, verbose_name='Danh mục')
    hinh_anh = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='Hình ảnh')

    class Meta:
        verbose_name = 'Sản phẩm'
        verbose_name_plural = 'Sản phẩm'
        ordering = ['ma_san_pham']

    def __str__(self):
        return f"{self.ma_san_pham} - {self.ten_san_pham}"

    @property
    def trang_thai_ton_kho(self):
        if self.ton_kho == 0:
            return 'het_hang'
        elif self.ton_kho < 10:
            return 'thap'
        else:
            return 'day_du'

    @property
    def trang_thai_ton_kho_display(self):
        mapping = {
            'het_hang': 'Hết hàng',
            'thap': 'Thấp',
            'day_du': 'Đầy đủ',
        }
        return mapping.get(self.trang_thai_ton_kho, '')
