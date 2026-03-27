from django.urls import path
from . import views

app_name = 'quanlysanpham'

urlpatterns = [
    path('', views.danhsachsanpham, name='danhsachsanpham'),
    path('danh-sach/', views.danhsachsanpham, name='danhsachsanpham_alt'),
    path('chi-tiet/<int:sanpham_id>/', views.chitietsanpham, name='chitietsanpham'),
]
