from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='trangchu'),
    path('xem-san-pham/', views.xem_san_pham, name='xem_san_pham'),
    path('chi-tiet-san-pham/', views.chi_tiet_san_pham, name='chi_tiet_san_pham'),
    path('so-sanh-san-pham/', views.so_sanh_san_pham, name='so_sanh_san_pham'),
    path('frame-chon-san-pham/', views.frame_chon_san_pham, name='frame_chon_san_pham'),
]
