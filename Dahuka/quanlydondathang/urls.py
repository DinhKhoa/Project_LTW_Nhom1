from django.urls import path
from . import views

app_name = 'quanlydondathang'

urlpatterns = [
    path('', views.danh_sach_don_hang, name='danh_sach'),
    path('<int:pk>/', views.chi_tiet_don_hang, name='chi_tiet'),
]
