from django.urls import path
from . import views

app_name = 'quanlynhiemvu'

urlpatterns = [
    path('', views.danh_sach_nhiem_vu, name='danh_sach'),
    path('chi-tiet/', views.chi_tiet_nhiem_vu, name='chi_tiet_lap_dat'),
]
