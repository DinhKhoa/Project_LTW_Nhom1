from django.contrib.auth.decorators import user_passes_test

# --- DECORATOR PHÂN QUYỀN TRONG HỆ THỐNG ---

# 1. Yêu cầu quyền NHÂN VIÊN (Staff)
def staff_required(view_func):
    """
    Chỉ cho phép Nhân viên (is_staff) đã kích hoạt tài khoản được truy cập.
    Thường dùng cho các trang xử lý đơn hàng, danh sách công việc.
    """
    def is_staff(u):
        return u.is_active and u.is_staff

    actual_decorator = user_passes_test(
        is_staff,
        login_url="core:home" # Nếu không phải staff -> Đẩy về trang chủ
    )
    return actual_decorator(view_func)


# 2. Yêu cầu quyền ADMIN TỐI CAO (Superuser)
def admin_required(view_func):
    """
    Chỉ cho phép Admin (is_superuser) đã kích hoạt tài khoản được truy cập.
    Dùng cho các trang nhạy cảm như Thống kê doanh thu, Cấu hình hệ thống.
    """
    def is_admin(u):
        return u.is_active and u.is_superuser

    actual_decorator = user_passes_test(
        is_admin,
        login_url="core:home" # Nếu không phải admin -> Đẩy về trang chủ
    )
    return actual_decorator(view_func)
