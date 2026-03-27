# Hệ Thống Quản Lý Tài Khoản Dahuka

## Tính Năng Chính

Hệ thống gồm 3 module chính:

### 1. Sổ Địa Chỉ (Address Book)
- ✅ **Thêm Địa Chỉ**: Click vào nút "Thêm địa chỉ" để mở overlay form
  - Nhập thông tin: Số điện thoại, tên, email, tỉnh/thành phố, quận/huyện, phường/xã, địa chỉ
  - Chọn loại địa chỉ (mặc định: Nhà riêng/Chung cư)
  - Hover buttons: Trắng→Đen (Xác nhận), Đen→Trắng (Hủy)
  - Click X để đóng mà không lưu
  - Sau xác nhận: Hiển thị thông báo thành công 2 giây, sau đó hiển thị danh sách địa chỉ

- ✅ **Chỉnh Sửa Địa Chỉ**: Click nút "Chỉnh sửa" trên mỗi địa chỉ
  - Form được điền sẵn dữ liệu hiện tại
  - Nút thay đổi thành "Cập nhập"
  - Sau cập nhập thành công: Thông báo 2 giây, quay lại danh sách

- ✅ **Xóa Địa Chỉ**: Click nút "Xóa" trên mỗi địa chỉ
  - Mở overlay xác nhận với nền mờ
  - Nút "Hủy" (Đen→Trắng khi hover), Nút "Xác nhận" (Trắng→Đen khi hover)
  - Sau xóa: Thông báo 2 giây, danh sách cập nhập

### 2. Thông Tin Tài Khoản (Account Info)
- ✅ **Xem Thông Tin**: Hiển thị thông tin từ khi tạo tài khoản
  - Họ, Tên, Email, Số điện thoại
  - Biệt danh và Quốc tịch: Đã bỏ đi
  - Mật khẩu: Hiển thị ẩn, có nút "Cập nhập"

- ✅ **Lưu Thay Đổi**: Click "Lưu thay đổi"
  - Validate thông tin
  - Thông báo "Lưu thông tin thành công"

- ✅ **Đổi Mật Khẩu**: Click nút "Cập nhập" bên cạnh mật khẩu
  - Bước 1: Nhập mật khẩu mới + xác nhận
  - Bước 2: Nhập mật khẩu cũ để xác thực
  - Thông báo "Cập nhập mật khẩu thành công"

### 3. Quản Lý Đơn Hàng (Order Management)
- ✅ **Danh Sách Đơn Hàng**: Hiển thị tất cả đơn hàng
  - Mã đơn, Trạng thái, Ngày đặt, Tổng tiền
  - Nút "Xem chi tiết" và "Hủy đơn hàng" (chỉ khi pending/processing)

- ✅ **Xem Chi Tiết**: Click "Xem chi tiết"
  - Hiển thị overlay với:
    - Mã đơn, Trạng thái, Ngày đặt
    - Thông tin người nhận
    - Danh sách sản phẩm với số lượng, giá
    - Tổng tiền
    - (Nếu đã hủy) Lý do hủy

- ✅ **Hủy Đơn Hàng**: Click "Hủy đơn hàng"
  - Mở overlay form nhập lý do hủy
  - Validate: Không được để trống
  - Thông báo "Hủy đơn hàng thành công"
  - Danh sách cập nhập

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

## Validation

- **Số điện thoại**: 10-11 chữ số
- **Email**: Format hợp lệ
- **Bắt buộc**: Tên, SĐT, Email, Địa chỉ, Tỉnh, Quận, Phường
- **Xác nhận**: Mật khẩu mới phải khớp với xác nhận

## Cấu Trúc Thư Mục

```
Dahuka/
├── templates/
│   ├── base.html              # Layout chính
│   ├── login.html             # Trang đăng nhập
│   └── account/
│       └── dashboard.html     # Trang quản lý tài khoản
├── static/
│   ├── img/                   # Hình ảnh
│   └── js/
│       └── account.js         # Logic JavaScript
├── trangchu/
│   ├── models.py              # Customer, Address, Order, OrderItem
│   ├── views.py               # API views + Auth views
│   ├── admin.py               # Django admin config
│   └── migrations/
├── Dahuka/
│   ├── urls.py                # URL routing
│   ├── settings.py            # Django config
│   └── wsgi.py
└── manage.py
```

## Ghi Chú

- Tất cả thao tác đều yêu cầu đăng nhập
- Dữ liệu được lưu trên server
- API endpoints trả về JSON
- CSRF token được xử lý tự động
- LocalStorage không được dùng (tất cả từ server)

## Tác Giả

Nhóm phát triển Dahuka - Dự án lập trình web

