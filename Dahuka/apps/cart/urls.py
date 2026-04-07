from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart, name='cart'),
    path('add/', views.add_product_to_cart, name='add_product_to_cart'),
]
