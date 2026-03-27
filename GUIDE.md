# Hướng Dẫn Chi Tiết - Hệ Thống Quản Lý Tài Khoản Dahuka

## 📋 Mục Lục
1. [Tính Năng Chính](#tính-năng-chính)
2. [Hướng Dẫn Sử Dụng](#hướng-dẫn-sử-dụng)
3. [Cấu Trúc Dự Án](#cấu-trúc-dự-án)
4. [API Documentation](#api-documentation)
5. [Troubleshooting](#troubleshooting)

---

## 🎯 Tính Năng Chính

### 1. Sổ Địa Chỉ 📍

**Màn Hình Chính - Danh Sách Địa Chỉ**
- Hiển thị danh sách tất cả địa chỉ đã lưu
- Nút "+ Thêm địa chỉ" ở góc trên cùng
- Mỗi địa chỉ có 2 nút: "Chỉnh sửa" và "Xóa"

**Chức Năng: Thêm Địa Chỉ**
```
Flow: Click "+ Thêm" → Mở Modal Overlay (nền mờ) → 
      Nhập thông tin → Xác nhận → Thông báo thành công 2s → 
      Cập nhập danh sách
```

Fields cần nhập:
- Họ và tên (*)
- Số điện thoại (*) - 10-11 chữ số
- Email (*) - Định dạng email hợp lệ
- Tỉnh/Thành phố (*)
- Quận/Huyện (*)
- Phường/Xã (*)
- Địa chỉ chi tiết (*) - Có thể nhập địa chỉ dài
- Loại địa chỉ - Dropdown (Mặc định: Nhà riêng/Chung cư)

Hover Effects:
- Nút "Xác nhận": Trắng/Border → Đen/White text (0.3s)
- Nút "Hủy": Đen → Trắng/Black text (0.3s)
- Click X: Đóng modal không lưu

**Chức Năng: Chỉnh Sửa Địa Chỉ**
```
Flow: Click "Chỉnh sửa" → Modal điền sẵn dữ liệu → 
      Chỉnh sửa → Nút "Cập nhập" → Thông báo thành công 2s
```

**Chức Năng: Xóa Địa Chỉ**
```
Flow: Click "Xóa" → Modal xác nhận → 
      Click "Xác nhận" → Thông báo thành công 2s → Cập nhập danh sách
```

---

### 2. Thông Tin Tài Khoản 👤

**Màn Hình Chính - Thông Tin Cá Nhân**

Hiển thị thông tin:
- Họ (*)
- Tên (*)
- Email (*)
- Số điện thoại
- Mật khẩu (Ẩn, có nút "Cập nhập")

Đã bỏ:
- ~~Biệt danh~~ ❌
- ~~Quốc tịch~~ ❌

**Chức Năng: Lưu Thay Đổi**
```
Flow: Chỉnh sửa thông tin → Click "Lưu thay đổi" → 
      Validate → Thông báo "Lưu thông tin thành công"
```

**Chức Năng: Đổi Mật Khẩu (2 Bước)**

Bước 1:
```
Click "Cập nhập" (bên Mật khẩu) → Modal "Thay đổi mật khẩu" →
Nhập:
  - Mật khẩu mới (*)
  - Xác nhận mật khẩu mới (*)
→ Click "Xác nhận"
```

Bước 2:
```
Modal "Xác thực mật khẩu cũ" →
Nhập mật khẩu cũ (*) →
Click "Xác nhận" →
Nếu đúng: Thông báo "Cập nhập mật khẩu thành công"
Nếu sai: Hiển thị lỗi "Mật khẩu cũ không đúng"
```

---

### 3. Quản Lý Đơn Hàng 📦

**Màn Hình Chính - Danh Sách Đơn Hàng**

Mỗi đơn hàng hiển thị:
- Mã đơn (VD: DH20260122008)
- Trạng thái (Badge với màu khác nhau)
  - Chờ xác nhận (vàng)
  - Đang xử lý (xanh nhạt)
  - Đang giao hàng (xanh dương)
  - Đã giao (xanh lá)
  - Đã hủy (đỏ)
- Ngày đặt đơn
- Tổng tiền
- 2 nút: "Xem chi tiết" và "Hủy đơn hàng" (chỉ khi pending/processing)

**Chức Năng: Xem Chi Tiết**
```
Flow: Click "Xem chi tiết" → Modal Overlay →
Hiển thị:
  - Mã đơn + Trạng thái + Ngày đặt
  - Thông tin người nhận (Họ tên, SĐT, Email, Địa chỉ)
  - Danh sách sản phẩm (Tên, Số lượng, Giá)
  - Tổng tiền
  - (Nếu hủy) Lý do hủy
```

**Chức Năng: Hủy Đơn Hàng**
```
Flow: Click "Hủy đơn hàng" (chỉ khi pending/processing) →
Modal "Lý do hủy đơn hàng" →
Nhập lý do (*) →
Click "Xác nhận hủy" →
Thông báo "Hủy đơn hàng thành công" →
Cập nhập danh sách (trạng thái → Đã hủy) →
Chi tiết đơn hiển thị lý do hủy
```

---

## 🚀 Hướng Dẫn Sử Dụng

### Cài Đặt Ban Đầu

```bash
# 1. Di chuyển vào thư mục dự án
cd C:\Users\ASUS\Project_LTW_Nhom1\Dahuka

# 2. Kích hoạt Virtual Environment
.\.venv\Scripts\activate

# 3. Cài đặt Django (nếu chưa có)
pip install django

# 4. Chạy migrations (tạo database)
python manage.py migrate

# 5. Tạo dữ liệu sample
python create_sample_data.py

# 6. Khởi động server
python manage.py runserver
```

### Truy Cập Ứng Dụng

```
Trang chính:           http://localhost:8000/
Đăng nhập:             http://localhost:8000/login/
Quản lý tài khoản:     http://localhost:8000/account/
Django Admin:          http://localhost:8000/admin/
```

### Tài Khoản Demo

```
Username: testuser
Password: password123
Email: test@example.com
```

### Tài Khoản Admin

```bash
# Tạo tài khoản admin
python manage.py createsuperuser

# Theo dõi
Username: admin
Password: (nhập mật khẩu của bạn)
Email: admin@example.com
```

---

## 📁 Cấu Trúc Dự Án

```
Dahuka/
│
├── templates/
│   ├── base.html                    # Template layout chính
│   ├── login.html                   # Trang đăng nhập
│   └── account/
│       └── dashboard.html           # Dashboard quản lý tài khoản
│
├── static/
│   ├── img/                         # Hình ảnh sản phẩm
│   │   ├── LOGO.png
│   │   ├── BANNER.png
│   │   └── ...
│   └── js/
│       └── account.js               # JavaScript logic cho dashboard
│
├── trangchu/
│   ├── models.py                    # Customer, Address, Order, OrderItem
│   ├── views.py                     # Views + API endpoints
│   ├── admin.py                     # Django admin configuration
│   ├── urls.py                      # URL routing
│   └── migrations/                  # Database migrations
│
├── Dahuka/
│   ├── settings.py                  # Django settings
│   ├── urls.py                      # Main URL configuration
│   ├── wsgi.py                      # WSGI config
│   └── asgi.py                      # ASGI config
│
├── db.sqlite3                       # Database file
├── manage.py                        # Django management script
├── create_sample_data.py            # Script tạo dữ liệu sample
├── test.py                          # Test script
└── README.md                        # Tài liệu dự án
```

---

## 🔌 API Documentation

### Authentication
Tất cả API endpoints yêu cầu:
- User phải đăng nhập
- CSRF token (tự động xử lý)

### Endpoints

#### Profile APIs

**GET /api/profile/** - Lấy thông tin tài khoản
```javascript
// Response
{
  "success": true,
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "first_name": "An",
    "last_name": "Nguyễn Văn",
    "get_full_name": "An Nguyễn Văn"
  },
  "customer": {
    "id": 1,
    "phone": "0934943950"
  }
}
```

**PUT /api/profile/** - Cập nhập thông tin
```javascript
// Request
{
  "first_name": "An",
  "last_name": "Nguyễn Văn",
  "email": "test@example.com",
  "phone": "0934943950"
}

// Response
{
  "success": true,
  "message": "Cập nhập thành công"
}
```

**POST /api/change-password/** - Đổi mật khẩu
```javascript
// Request
{
  "old_password": "password123",
  "new_password": "newpassword123"
}

// Response
{
  "success": true,
  "message": "Cập nhập mật khẩu thành công"
}
```

#### Address APIs

**GET /api/addresses/** - Danh sách địa chỉ
```javascript
// Response
{
  "success": true,
  "addresses": [
    {
      "id": 1,
      "full_name": "An Nguyễn Văn",
      "phone": "0934943950",
      "email": "an@example.com",
      "province": "Thành phố Đà Nẵng",
      "district": "Quận Sơn Trà",
      "ward": "Phường Phước Mỹ",
      "address_detail": "68 Đường Khuê",
      "address_type": "home",
      "is_default": true
    }
  ]
}
```

**POST /api/addresses/** - Thêm địa chỉ
```javascript
// Request
{
  "full_name": "An Nguyễn Văn",
  "phone": "0934943950",
  "email": "an@example.com",
  "province": "Thành phố Đà Nẵng",
  "district": "Quận Sơn Trà",
  "ward": "Phường Phước Mỹ",
  "address_detail": "68 Đường Khuê",
  "address_type": "home",
  "is_default": false
}

// Response
{
  "success": true,
  "message": "Thêm địa chỉ thành công"
}
```

**PUT /api/addresses/<id>/** - Cập nhập địa chỉ
```javascript
// Request (tương tự POST)
// Response
{
  "success": true,
  "message": "Cập nhập địa chỉ thành công"
}
```

**DELETE /api/addresses/<id>/** - Xóa địa chỉ
```javascript
// Response
{
  "success": true,
  "message": "Xóa địa chỉ thành công"
}
```

#### Order APIs

**GET /api/orders/** - Danh sách đơn hàng
```javascript
// Response
{
  "success": true,
  "orders": [
    {
      "id": 1,
      "order_number": "DH20260122008",
      "total_amount": 11645000,
      "status": "pending",
      "created_at": "2026-01-22T10:28:00Z",
      "address": { /* address object */ }
    }
  ]
}
```

**GET /api/orders/<id>/** - Chi tiết đơn hàng
```javascript
// Response
{
  "success": true,
  "order": {
    "id": 1,
    "order_number": "DH20260122008",
    "total_amount": 11645000,
    "status": "pending",
    "cancel_reason": "",
    "created_at": "2026-01-22T10:28:00Z",
    "address": { /* address object */ },
    "items": [
      {
        "id": 1,
        "product_name": "Máy Lọc Nước RO 12 Cấp",
        "quantity": 1,
        "unit_price": 11645000
      }
    ]
  }
}
```

**POST /api/orders/<id>/cancel/** - Hủy đơn hàng
```javascript
// Request
{
  "cancel_reason": "Tôi không cần sản phẩm này nữa"
}

// Response
{
  "success": true,
  "message": "Hủy đơn hàng thành công"
}
```

---

## 🐛 Troubleshooting

### Lỗi: "ModuleNotFoundError: No module named 'django'"
```bash
# Giải pháp:
pip install django
```

### Lỗi: "TemplateDoesNotExist: account/dashboard.html"
```bash
# Kiểm tra folder templates tồn tại:
# C:\Users\ASUS\Project_LTW_Nhom1\Dahuka\templates\account\
```

### Lỗi: CSRF token bị từ chối
```bash
# Đảm bảo:
# 1. {% csrf_token %} có trong form
# 2. CSRF middleware enabled trong settings.py
# 3. Request gửi từ cùng domain
```

### Lỗi: API trả về 403 Forbidden
```bash
# Nguyên nhân: User chưa đăng nhập
# Giải pháp: Đăng nhập trước khi truy cập /account/
```

### Lỗi: Database khóa (Locked database)
```bash
# Giải pháp: Xóa db.sqlite3 và chạy migrate lại
rm db.sqlite3
python manage.py migrate
python create_sample_data.py
```

---

## 📝 Ghi Chú Quan Trọng

1. **Security**: Dự án hiện ở chế độ DEBUG=True. Bỏ cảnh báo bảo mật này khi deploy!

2. **Static Files**: Khi deploy, chạy:
   ```bash
   python manage.py collectstatic
   ```

3. **Thời gian Session**: Mặc định là 2 tuần. Có thể thay đổi trong settings.py

4. **Validation**: 
   - Email phải hợp lệ
   - Số điện thoại phải 10-11 chữ số
   - Mật khẩu mới phải khớp xác nhận

5. **Thông báo Auto-close**: Tất cả thông báo tự đóng sau 2 giây

---

## ❓ FAQ

**Q: Làm sao để reset password?**
A: Dùng Django admin hoặc chạy:
```bash
python manage.py changepassword testuser
```

**Q: Có thể thêm nhiều địa chỉ không?**
A: Có, không có giới hạn. Địa chỉ đầu tiên sẽ mặc định là địa chỉ mặc định.

**Q: Làm sao xóa dữ liệu test?**
A: Xóa db.sqlite3 và chạy:
```bash
python manage.py migrate
python create_sample_data.py
```

**Q: Có thể chỉnh sửa trạng thái đơn hàng không?**
A: Chỉ admin mới có thể. Vào /admin/

---

## 📞 Liên Hệ & Hỗ Trợ

Nếu có vấn đề, kiểm tra:
1. Console của browser (F12)
2. Terminal của server (kiểm tra error messages)
3. Django admin để xem dữ liệu

Happy coding! 🚀

