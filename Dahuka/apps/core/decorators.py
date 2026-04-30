from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect

def staff_required(view_func):
    """Decorator for views that checks that the user is logged in and is a staff member."""
    def is_staff(u):
        return u.is_active and u.is_staff
    
    actual_decorator = user_passes_test(
        is_staff,
        login_url='core:home' # Redirect to home if not staff
    )
    return actual_decorator(view_func)

def admin_required(view_func):
    """Decorator for views that checks that the user is logged in and is a superuser."""
    def is_admin(u):
        return u.is_active and u.is_superuser
    
    actual_decorator = user_passes_test(
        is_admin,
        login_url='core:home' # Redirect to home if not admin
    )
    return actual_decorator(view_func)
