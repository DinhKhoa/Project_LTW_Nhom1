from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def customer_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_staff or request.user.is_superuser:
            messages.warning(request, "Tài khoản nhân viên/admin không thể truy cập mục này.")
            return redirect('account:profile_view')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
