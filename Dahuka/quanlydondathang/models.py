from django.db import models
from quanlydanhmuc.models import SanPham


class DonDatHang(models.Model):
    TRANG_THAI_CHOICES = [
        ('cho_xac_nhan', 'Chờ xác nhận'),
        ('da_xac_nhan', 'Đã xác nhận'),
        ('dang_giao_hang', 'Đang giao hàng'),
        ('giao_hang_thanh_cong', 'Giao hàng thành công'),
        ('da_huy', 'Đã hủy'),
    ]

    HINH_THUC_THANH_TOAN = [
        ('tien_mat', 'Tiền mặt'),
        ('chuyen_khoan', 'Chuyển khoản'),
        ('the_tin_dung', 'Thẻ tín dụng'),
    ]

    TRANG_THAI_THANH_TOAN = [
        ('chua_thanh_toan', 'Chưa thanh toán'),
        ('da_thanh_toan', 'Đã thanh toán'),
    ]

    ma_don_hang = models.CharField(max_length=30, unique=True, verbose_name='Mã đơn hàng')
    ngay_dat_don = models.DateTimeField(auto_now_add=True, verbose_name='Ngày đặt đơn')
    ho_ten = models.CharField(max_length=200, verbose_name='Họ tên')
    so_dien_thoai = models.CharField(max_length=20, verbose_name='Số điện thoại')
    dia_chi = models.TextField(verbose_name='Địa chỉ')
    trang_thai = models.CharField(max_length=30, choices=TRANG_THAI_CHOICES, default='cho_xac_nhan', verbose_name='Trạng thái')
    hinh_thuc_thanh_toan = models.CharField(max_length=20, choices=HINH_THUC_THANH_TOAN, default='tien_mat', verbose_name='Hình thức thanh toán')
    trang_thai_thanh_toan = models.CharField(max_length=20, choices=TRANG_THAI_THANH_TOAN, default='chua_thanh_toan', verbose_name='Trạng thái thanh toán')
    tien_coc = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name='Tiền cọc')
    nhan_vien_phu_trach = models.CharField(max_length=200, blank=True, verbose_name='Nhân viên phụ trách')

    class Meta:
        verbose_name = 'Đơn đặt hàng'
        verbose_name_plural = 'Đơn đặt hàng'
        ordering = ['-ngay_dat_don']

    def __str__(self):
        return self.ma_don_hang

    @property
    def tong_tien_hang(self):
        total = sum(item.thanh_tien for item in self.chitietdonhang_set.all())
        return total

    @property
    def thanh_tien(self):
        return self.tong_tien_hang - self.tien_coc


class ChiTietDonHang(models.Model):
    don_hang = models.ForeignKey(DonDatHang, on_delete=models.CASCADE, verbose_name='Đơn hàng')
    san_pham = models.ForeignKey(SanPham, on_delete=models.CASCADE, verbose_name='Sản phẩm')
    so_luong = models.IntegerField(default=1, verbose_name='Số lượng')
    don_gia = models.DecimalField(max_digits=15, decimal_places=0, verbose_name='Đơn giá')

    class Meta:
        verbose_name = 'Chi tiết đơn hàng'
        verbose_name_plural = 'Chi tiết đơn hàng'

    def __str__(self):
        return f"{self.don_hang.ma_don_hang} - {self.san_pham.ten_san_pham}"

    @property
    def thanh_tien(self):
        return self.so_luong * self.don_gia
