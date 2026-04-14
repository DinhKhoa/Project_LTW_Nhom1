from django.urls import path
from . import views

app_name = 'promotions'

urlpatterns = [
    path('chi-tiet/', views.chi_tiet_khuyen_mai, name='chi_tiet_khuyen_mai'),
    path('', views.danh_sach_khuyen_mai, name='quan_ly_khuyen_mai'),
    path('them-khuyen-mai/', views.them_khuyen_mai, name='quan_ly_khuyen_mai'),
]
