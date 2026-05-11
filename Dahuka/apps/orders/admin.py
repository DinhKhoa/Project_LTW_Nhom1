from django.contrib import admin
from .models import Order, OrderItem

# ==============================================================================
# ADMIN CONFIGURATION: QUẢN TRỊ ĐƠN HÀNG TRÊN TRANG HỆ THỐNG (/admin)
# ==============================================================================

class OrderItemInline(admin.TabularInline):
    """
    Nhúng danh sách sản phẩm trực tiếp vào trang chi tiết đơn hàng.
    Giúp Admin không phải chuyển qua lại giữa các bảng dữ liệu.
    """
    model = OrderItem
    extra = 0  # Không hiện thêm các dòng trống thừa thãi
    fields = ("product", "quantity", "price", "warranty_expiration")
    # Ngày bảo hành được tính tự động, không cho phép Admin sửa thủ công để đảm bảo tính chính xác
    readonly_fields = ("warranty_expiration",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Cấu hình giao diện quản lý Đơn hàng chuyên nghiệp cho Admin.
    """
    # 1. Các cột thông tin quan trọng hiện ra ở trang danh sách
    list_display = (
        "order_code",
        "full_name",
        "phone",
        "total_amount",
        "status",
        "created_at",
    )
    
    # 2. Các bộ lọc nhanh ở cột bên phải (Theo trạng thái và ngày tháng)
    list_filter = ("status", "created_at")
    
    # 3. Thanh tìm kiếm thông minh (Tìm theo mã đơn, tên hoặc số điện thoại)
    search_fields = ("order_code", "full_name", "phone")
    
    # 4. Các trường chỉ cho phép xem, không cho sửa
    readonly_fields = ("order_code", "created_at", "updated_at")
    
    # 5. Nhúng bảng sản phẩm (OrderItem) vào giao diện
    inlines = [OrderItemInline]

    def save_model(self, request, obj, form, change):
        """
        Ghi đè hành động Lưu của Admin để đồng bộ hóa với Business Logic.
        Nếu Admin chuyển đơn hàng sang 'Hoàn thành' ngay trong trang Admin,
        hệ thống vẫn phải tự động kích hoạt bảo hành sản phẩm.
        """
        super().save_model(request, obj, form, change)
        
        if obj.status == "completed":
            from .services import OrderService
            # Gọi lại service để xử lý logic bảo hành (DRY - Don't Repeat Yourself)
            OrderService.process_warranty(obj)
