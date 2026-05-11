# --- HẰNG SỐ CỦA HỆ THỐNG ---

# Cấu hình phân trang
DEFAULT_PAGE_SIZE = 10 # Số lượng sản phẩm hiển thị trên 1 trang mặc định
ADMIN_PAGE_SIZE = 10   # Số lượng mục hiển thị trong trang quản trị

# Cấu hình Giỏ hàng & Đặt cọc
CART_DEFAULT_DEPOSIT_PERCENT = 10 # Phần trăm đặt cọc mặc định (10%)
CART_MIN_DEPOSIT_PERCENT = 10     # Phần trăm đặt cọc tối thiểu
CART_MAX_DEPOSIT_PERCENT = 50     # Phần trăm đặt cọc tối đa

# Cấu hình Vận chuyển mặc định
DEFAULT_DELIVERY_CITY = "Đà Nẵng"
DEFAULT_DELIVERY_DAYS = 3 # Số ngày giao hàng dự kiến

# Cấu hình Kiểm tra dữ liệu (Validation)
PHONE_FORMAT_REGEX = r'^[0-9]{10,11}$' # Biểu thức chính quy kiểm tra SĐT
PHONE_MIN_LENGTH = 10
PHONE_MAX_LENGTH = 11
