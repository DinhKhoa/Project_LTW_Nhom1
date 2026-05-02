from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect


def staff_required(view_func):
    def is_staff(u):
        return u.is_active and u.is_staff

    actual_decorator = user_passes_test(
        is_staff,
        login_url="core:home"
    )
    return actual_decorator(view_func)


def admin_required(view_func):
    def is_admin(u):
        return u.is_active and u.is_superuser

    actual_decorator = user_passes_test(
        is_admin,
        login_url="core:home"
    )
    return actual_decorator(view_func)
