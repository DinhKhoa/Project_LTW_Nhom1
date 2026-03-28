"""
URL configuration for Dahuka project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from trangchu import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="trangchu"),
    path("login/", views.DahukaLoginView.as_view(), name="login"),
    path("logout/", views.DahukaLogoutView.as_view(), name="logout"),
    path("Account/", include("Account.urls")),
    
    # Legacy/Moved path if needed for redirect, but better use include
    # path("Account/", views.account_dashboard, name="account_dashboard"),
    
    path("xem-san-pham/", views.xem_san_pham, name="xem_san_pham"),
    path("chi-tiet-san-pham/", views.chi_tiet_san_pham, name="chi_tiet_san_pham_customer"),
    path("so-sanh-san-pham/", views.so_sanh_san_pham, name="so_sanh_san_pham"),
    
    # Restored App Routes
    path('quanlysanpham/', include('quanlysanpham.urls')),
    path('quanlydanhmuc/', include('quanlydanhmuc.urls')),
    path('quanlydondathang/', include('quanlydondathang.urls')),
    path('quanlykhuyenmai/', include('quanlykhuyenmai.urls')),
    path('quanlygiohang/', include('quanlygiohang.urls')),
    path('quanlynhiemvu/', include('quanlynhiemvu.urls')),
    path('diembanbaohanh/', include('diembanbaohanh.urls')),
    
]
