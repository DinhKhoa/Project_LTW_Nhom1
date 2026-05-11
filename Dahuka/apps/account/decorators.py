from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


# ==============================================================================
# ĐỊNH NGHĨA CUSTOM DECORATOR (Anh bảo vệ tự chế)
# ==============================================================================
def customer_required(view_func):
    """
    Decorator này dùng để CHỈ cho phép Khách hàng truy cập.
    Nếu Admin hoặc Nhân viên 'đi lạc' vào thì sẽ bị chặn lại.
    """

    @wraps(view_func)  # Giữ lại các thông tin gốc của hàm (tên hàm, metadata...)
    def _wrapped_view(request, *args, **kwargs):
        # --- BƯỚC 1: KIỂM TRA (HÀNH ĐỘNG CỦA BẢO VỆ) ---
        if request.user.is_staff or request.user.is_superuser:
            # Nếu là nhân viên hoặc admin -> Thông báo và đẩy ra trang cá nhân
            messages.warning(
                request, "Tài khoản nhân viên/admin không thể truy cập mục này."
            )
            return redirect("account:profile_view")

        # --- BƯỚC 2: CHO PHÉP (VÀO TIỆC) ---
        # Nếu là khách hàng bình thường -> Cho phép chạy tiếp hàm view_func gốc
        return view_func(request, *args, **kwargs)

    return _wrapped_view
