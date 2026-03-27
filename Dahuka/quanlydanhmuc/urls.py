from django.urls import path
from . import views

app_name = 'quanlydanhmuc'

urlpatterns = [
    path('', views.danh_sach_danh_muc, name='danh_sach'),
    path('them/', views.them_danh_muc, name='them'),
    path('sua/<int:pk>/', views.sua_danh_muc, name='sua'),
    path('xoa/<int:pk>/', views.xoa_danh_muc, name='xoa'),
    path('san-pham/<int:pk>/', views.chi_tiet_san_pham_theo_danh_muc, name='san_pham_theo_danh_muc'),
]
