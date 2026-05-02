# Web bán sản phẩm chăm sóc nước Dahuka

## Giới Thiệu

Dahuka là hệ thống thương mại điện tử chuyên về sản phẩm máy lọc nước và cây nước nóng lạnh, được xây dựng bằng Django 6.0. Hệ thống cung cấp đầy đủ các tính năng từ quản lý sản phẩm, giỏ hàng, đặt hàng đến quản lý tài khoản khách hàng.

## Tính Năng Chính

### 1. Quản Lý Sản Phẩm (Products)

- ✅ Hiển thị danh sách sản phẩm theo danh mục
- ✅ Chi tiết sản phẩm với thông số kỹ thuật đầy đủ
- ✅ Thư viện ảnh sản phẩm (ảnh chính, ảnh thông số, ảnh tính năng, ảnh mô tả)
- ✅ Quản lý tồn kho và trạng thái sản phẩm
- ✅ Sản phẩm nổi bật hiển thị trên trang chủ
- ✅ Tìm kiếm và lọc sản phẩm

### 2. Danh Mục Sản Phẩm (Categories)

- ✅ Cấu trúc danh mục phân cấp
- ✅ Lọc sản phẩm theo danh mục
- ✅ Quản lý mã danh mục và slug

### 3. Giỏ Hàng (Cart)

- ✅ Thêm/xóa/cập nhật số lượng sản phẩm
- ✅ Hỗ trợ giỏ hàng cho cả user đã đăng nhập và guest (session)
- ✅ Tính tổng tiền tự động
- ✅ Hiển thị số lượng sản phẩm trong giỏ hàng

### 4. Đặt Hàng (Orders)

- ✅ Tạo đơn hàng với thông tin giao hàng đầy đủ
- ✅ Mã đơn hàng tự động (format: DHK-YYYYMMDD-XXXXX)
- ✅ Quản lý trạng thái đơn hàng: Chờ xử lý → Đã xác nhận → Đang giao → Hoàn thành/Hủy
- ✅ Hỗ trợ thanh toán toàn bộ hoặc đặt cọc
- ✅ Phân công nhân viên phụ trách đơn hàng
- ✅ Ghi chú và ảnh minh chứng
- ✅ Hủy đơn hàng với lý do

### 5. Quản Lý Tài Khoản (Account)

#### 5.1. Thông Tin Cá Nhân

- ✅ Xem và cập nhật thông tin: Họ, Tên, Email, Số điện thoại, Giới tính, Ngày sinh
- ✅ Đổi mật khẩu với xác thực mật khẩu cũ
- ✅ Thông báo thành công/lỗi với hiệu ứng mượt mà

#### 5.2. Sổ Địa Chỉ

- ✅ **Thêm Địa Chỉ**: Form overlay với đầy đủ thông tin
  - Tên người nhận, Số điện thoại
  - Tỉnh/Thành phố, Quận/Huyện, Phường/Xã, Địa chỉ chi tiết
  - Loại địa chỉ: Nhà riêng/Chung cư, Văn phòng, Khác
  - Đặt làm địa chỉ mặc định
- ✅ **Chỉnh Sửa Địa Chỉ**: Form điền sẵn dữ liệu hiện tại
- ✅ **Xóa Địa Chỉ**: Xác nhận trước khi xóa
- ✅ **Địa Chỉ Mặc Định**: Tự động sử dụng khi đặt hàng

#### 5.3. Quản Lý Đơn Hàng

- ✅ **Danh Sách Đơn Hàng**: Xem tất cả đơn hàng đã đặt
  - Mã đơn hàng, Trạng thái, Ngày đặt, Tổng tiền
  - Lọc theo trạng thái
- ✅ **Chi Tiết Đơn Hàng**:
  - Thông tin người nhận và địa chỉ giao hàng
  - Danh sách sản phẩm với số lượng và giá
  - Tổng tiền và trạng thái thanh toán
  - Lý do hủy (nếu có)
- ✅ **Hủy Đơn Hàng**: Chỉ áp dụng cho đơn hàng ở trạng thái "Chờ xử lý" hoặc "Đã xác nhận"

### 6. Khuyến Mãi (Promotions)

- ✅ Quản lý các chương trình khuyến mãi
- ✅ Áp dụng giảm giá theo sản phẩm hoặc đơn hàng

### 7. Bảo Hành (Warranty)

- ✅ Quản lý thông tin bảo hành sản phẩm
- ✅ Theo dõi ngày hết hạn bảo hành

### 8. Công Việc (Tasks)

- ✅ Quản lý công việc nội bộ
- ✅ Phân công và theo dõi tiến độ

## Hướng Dẫn Sử Dụng

### 1. Cài Đặt

```bash
cd Dahuka
pip install django
python manage.py migrate
python create_sample_data.py
```

### 2. Khởi Động Server

```bash
python manage.py runserver
```

### 3. Truy Cập

- Trang chính: http://localhost:8000
- Đăng nhập: http://localhost:8000/login/
- Quản lý tài khoản: http://localhost:8000/account/

### 4. Tài Khoản Demo

- **Tên**: testuser
- **Mật khẩu**: password123

## Chi Tiết Kỹ Thuật

### Backend

- **Framework**: Django 6.0
- **Database**: SQLite (db.sqlite3)
- **Authentication**: Django Auth

### Models

1. **Customer**: OneToOne với User, lưu số điện thoại
2. **Address**: Foreign Key đến Customer, lưu thông tin địa chỉ
3. **Order**: Foreign Key đến Customer, lưu thông tin đơn hàng
4. **OrderItem**: Foreign Key đến Order, lưu chi tiết sản phẩm

### Frontend

- **CSS Framework**: Bootstrap 4
- **JavaScript**: Vanilla JS (không jQuery cho AJAX)
- **API Communication**: Fetch API với JSON
- **Notifications**: Custom toast notifications

### API Endpoints

```
GET    /api/profile/                    - Lấy thông tin tài khoản
PUT    /api/profile/                    - Cập nhập thông tin tài khoản
POST   /api/change-password/            - Đổi mật khẩu

GET    /api/addresses/                  - Danh sách địa chỉ
POST   /api/addresses/                  - Thêm địa chỉ
GET    /api/addresses/<id>/             - Chi tiết địa chỉ
PUT    /api/addresses/<id>/             - Cập nhập địa chỉ
DELETE /api/addresses/<id>/             - Xóa địa chỉ

GET    /api/orders/                     - Danh sách đơn hàng
GET    /api/orders/<id>/                - Chi tiết đơn hàng
POST   /api/orders/<id>/cancel/         - Hủy đơn hàng
```

## Tính Năng Hover Effects

Tất cả các nút đều có hover effects:

- **Nút Trắng/Border**: Trắng → Đen (text trắng)
- **Nút Đen**: Đen → Trắng (text đen)
- Transition mượt 0.3s

## Thông Báo

- **Thành công**: Xanh (#27ae60), tự đóng sau 2 giây
- **Lỗi**: Đỏ (#e74c3c), tự đóng sau 2 giây
- Hiệu ứng: Slide down vào, slide up ra

- **Xác nhận**: Mật khẩu mới phải khớp với xác nhận

## Cấu Trúc Thư Mục

```
Dahuka/
├── manage.py                          # Django management script
├── .gitignore                         # Git ignore rules
├── apps/                              # All Django apps
│   ├── account/                       # User account & addresses
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── api_views.py
│   │   ├── apps.py
│   │   ├── create_staff.py
│   │   ├── decorators.py
│   │   ├── forms.py
│   │   ├── models.py                  # Customer model
│   │   ├── selectors.py
│   │   ├── services.py
│   │   ├── signals.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── migrations/
│   │   ├── static/account/
│   │   └── templates/
│   ├── cart/                          # Shopping cart
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── context_processors.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── selectors.py
│   │   ├── services.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── migrations/
│   │   ├── static/cart/
│   │   ├── templates/
│   │   └── templatetags/
│   ├── categories/                    # Product categories
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── selectors.py
│   │   ├── services.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── migrations/
│   │   ├── static/
│   │   └── templates/
│   ├── core/                          # Core functionality
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── api_views.py
│   │   ├── apps.py
│   │   ├── constants.py
│   │   ├── context_processors.py
│   │   ├── decorators.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── selectors.py
│   │   ├── services.py
│   │   ├── urls.py
│   │   ├── utils.py
│   │   ├── views.py
│   │   ├── migrations/
│   │   ├── static/
│   │   └── templates/
│   ├── orders/                        # Orders management
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── selectors.py
│   │   ├── services.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── migrations/
│   │   ├── static/
│   │   └── templates/
│   ├── products/                      # Products catalog
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── selectors.py
│   │   ├── services.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── management/
│   │   ├── migrations/
│   │   ├── static/
│   │   └── templates/
│   ├── promotions/                    # Promotions & discounts
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── selectors.py
│   │   ├── services.py
│   │   ├── signals.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── management/
│   │   ├── migrations/
│   │   ├── static/
│   │   └── templates/
│   ├── tasks/                         # Internal tasks
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── selectors.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── migrations/
│   │   ├── static/
│   │   └── templates/
│   └── warranty/                      # Warranty management
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── models.py
│       ├── selectors.py
│       ├── services.py
│       ├── urls.py
│       ├── views.py
│       ├── migrations/
│       ├── static/
│       └── templates/
├── Dahuka/                            # Django project config
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── document/                          # Project docs
│   └── STRUCTURE.md
├── media/                             # Uploaded files
├── scratch/                           # Temporary files
├── static/                            # Static assets
└── templates/                         # Base templates
    ├── account_base.html
    ├── base.html
    ├── components/
    ├── partials/
    └── registration/
```

## Ghi Chú

- Tất cả thao tác đều yêu cầu đăng nhập
- Dữ liệu được lưu trên server
- API endpoints trả về JSON
- CSRF token được xử lý tự động
- LocalStorage không được dùng (tất cả từ server)

## Tác Giả

Dự án phát triển Dahuka - Dự án lập trình web **Nhom 1**
