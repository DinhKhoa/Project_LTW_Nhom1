from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('new/', views.product_detail, name='product_create'),
    path('<int:pk>/', views.product_detail, name='product_detail'),
    path('<int:pk>/toggle-visibility/', views.toggle_product_visibility, name='toggle_visibility'),
]
