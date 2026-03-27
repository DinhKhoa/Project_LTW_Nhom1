from django.contrib import admin
from django.urls import path
import sanpham.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', sanpham.views.danhsachsanpham, name='danhsachsanpham'),
    path('sanpham/<str:sanpham_id>/', sanpham.views.chitietsanpham, name='chitietsanpham'),
]
