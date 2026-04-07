import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

def index(request):
    return render(request, 'core/trangchu.html')


def xem_san_pham(request):
    return render(request, 'core/xem_san_pham.html')


def chi_tiet_san_pham(request):
    return render(request, 'core/chi_tiet_san_pham.html')


def so_sanh_san_pham(request):
    return render(request, 'core/so_sanh_san_pham.html')


def frame_chon_san_pham(request):
    return render(request, 'core/frame_chon_san_pham.html')


class DahukaLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True


class DahukaLogoutView(LogoutView):
    pass
