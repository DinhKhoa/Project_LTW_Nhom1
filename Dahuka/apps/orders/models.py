from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product
import random
from django.utils import timezone


# ==============================================================================
# MODEL: ĐƠN HÀNG (Order)
# ==============================================================================
class Order(models.Model):
    """
    Lưu trữ toàn bộ thông tin đơn hàng, thông tin thanh toán và trạng thái xử lý.
    Sử dụng ForeignKey để liên kết với User (Khách hàng và Nhân viên).
    """

    # Danh sách các trạng thái của một đơn hàng (Luồng vòng đời đơn hàng)
    STATUS_CHOICES = [
        ("pending", "Chờ xử lý"),      # Khách vừa đặt xong
        ("confirmed", "Đã xác nhận"),   # Admin đã gọi điện xác nhận
        ("processing", "Đang giao"),    # Đang trên đường vận chuyển
        ("completed", "Đã hoàn thành"), # Khách đã nhận hàng và trả tiền
        ("cancelled", "Đã hủy"),        # Đơn bị khách hoặc admin hủy
    ]

    # Mã định danh đơn hàng (VD: DHK-20240505-12345)
    order_code = models.CharField(
        max_length=50, unique=True, blank=True, null=True, verbose_name="Mã đơn hàng"
    )

    # Liên kết với User (Khách hàng) - null=True nếu khách đặt không cần tài khoản
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Khách hàng",
        null=True,
        blank=True,
    )

    # --- THÔNG TIN NGƯỜI NHẬN ---
    full_name = models.CharField(max_length=100, verbose_name="Họ tên người nhận")
    phone = models.CharField(max_length=15, verbose_name="Số điện thoại")
    city = models.CharField(max_length=100, verbose_name="Tỉnh/Thành phố", blank=True)
    district = models.CharField(max_length=100, verbose_name="Quận/Huyện", blank=True)
    ward = models.CharField(max_length=100, verbose_name="Phường/Xã", blank=True)
    house_details = models.CharField(
        max_length=255, verbose_name="Số nhà, tên đường", blank=True
    )

    # --- THÔNG TIN TÀI CHÍNH ---
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=0, verbose_name="Tổng tiền"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="Trạng thái",
    )

    # Hình thức: Trả hết 1 lần hoặc đặt cọc trước (Dành cho máy lọc nước đắt tiền)
    PAYMENT_METHOD_CHOICES = [
        ("full", "Thanh toán toàn bộ"),
        ("deposit", "Thanh toán cọc"),
    ]
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default="full",
        verbose_name="Hình thức thanh toán",
    )
    deposit_amount = models.DecimalField(
        max_digits=12, decimal_places=0, default=0, verbose_name="Số tiền cọc"
    )

    PAYMENT_STATUS_CHOICES = [
        ("chua_thanh_toan", "Chưa thanh toán"),
        ("da_thanh_toan", "Đã thanh toán"),
    ]
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="chua_thanh_toan",
        verbose_name="Trạng thái thanh toán",
    )

    # --- QUẢN TRỊ NỘI BỘ ---
    assigned_staff = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_orders",
        verbose_name="Nhân viên phụ trách",
    )
    note = models.TextField(
        verbose_name="Ghi chú của khách hàng", blank=True, null=True
    )
    cancel_reason = models.TextField(verbose_name="Lý do hủy", blank=True, null=True)
    proof_image = models.ImageField(
        upload_to="order_proofs/", blank=True, null=True, verbose_name="Ảnh minh chứng"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đặt")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Quản lý đơn hàng"

    @property
    def full_address(self):
        """Tự động ghép các trường địa chỉ thành 1 chuỗi hoàn chỉnh."""
        parts = [self.house_details, self.ward, self.district, self.city]
        return ", ".join([p for p in parts if p])

    @property
    def remaining_amount(self):
        """Tính số tiền còn lại phải thu (Tổng - Cọc)."""
        return self.total_amount - self.deposit_amount

    def save(self, *args, **kwargs):
        """
        Ghi đè hàm save để tự động tạo Mã đơn hàng (Order Code) duy nhất.
        Định dạng: DHK-YYYYMMDD-XXXXX (5 số ngẫu nhiên)
        """
        if not self.order_code:
            # 1. Lấy ngày hiện tại
            date_str = timezone.localtime().strftime("%Y%m%d")
            # 2. Tạo 5 số ngẫu nhiên
            rand_digits = "".join([str(random.randint(0, 9)) for _ in range(5)])
            self.order_code = f"DHK-{date_str}-{rand_digits}"
            
            # 3. Kiểm tra xem mã này đã tồn tại trong DB chưa (tránh trùng lặp 1 phần tỷ)
            while (
                Order.objects.filter(order_code=self.order_code)
                .exclude(pk=self.pk)
                .exists()
            ):
                rand_digits = "".join([str(random.randint(0, 9)) for _ in range(5)])
                self.order_code = f"DHK-{date_str}-{rand_digits}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id} - {self.full_name} ({self.order_code})"


# ==============================================================================
# MODEL: CHI TIẾT ĐƠN HÀNG (OrderItem)
# ==============================================================================
class OrderItem(models.Model):
    """
    Lưu trữ danh sách các sản phẩm cụ thể nằm trong một Đơn hàng.
    Một Đơn hàng (Order) có thể có nhiều Chi tiết (OrderItem).
    """
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", verbose_name="Đơn hàng"
    )
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, verbose_name="Sản phẩm"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Số lượng")
    
    # Lưu giá tại thời điểm mua (Tránh trường hợp sau này sản phẩm đổi giá làm sai lệch đơn cũ)
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Đơn giá")
    
    # Thời gian bảo hành (tính từ lúc mua)
    warranty_expiration = models.DateTimeField(
        blank=True, null=True, verbose_name="Ngày hết hạn bảo hành"
    )

    def __str__(self):
        return f"{self.product.name if self.product else 'N/A'} (x{self.quantity})"

    @property
    def get_total_price(self):
        """Tính thành tiền cho từng dòng sản phẩm (Đơn giá x Số lượng)."""
        return self.price * self.quantity
