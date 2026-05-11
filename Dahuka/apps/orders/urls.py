from django.urls import path
from . import views

# Nhóm URL cho app orders — tiền tố được đặt trong Dahuka/urls.py
app_name = 'orders'

urlpatterns = [
    path('', views.order_list, name='order_list'),         # Danh sách đơn hàng: /orders/
    path('<int:pk>/', views.order_detail, name='order_detail'),  # Chi tiết đơn hàng: /orders/1/
]
