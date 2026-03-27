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
from django.urls import path

import trangchu.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', trangchu.views.index, name='home'),
    path('xemsanpham/', trangchu.views.xem_san_pham, name='xem_san_pham'),
    path('chi-tiet-san-pham/', trangchu.views.chi_tiet_san_pham, name='chi_tiet_san_pham'),
    path('so-sanh-san-pham/', trangchu.views.so_sanh_san_pham, name='so_sanh_san_pham'),
    path('chi-tiet-khuyen-mai/', trangchu.views.chi_tiet_khuyen_mai, name='chi_tiet_khuyen_mai'),
    path('chon-san-pham/', trangchu.views.frame_chon_san_pham, name='frame_chon_san_pham'),
    path('cong-viec-lap-dat/', trangchu.views.cong_viec_lap_dat, name='cong_viec_lap_dat'),
    path('chi-tiet-lap-dat/', trangchu.views.chi_tiet_lap_dat, name='chi_tiet_lap_dat'),
]
