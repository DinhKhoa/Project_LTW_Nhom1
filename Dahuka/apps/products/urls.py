from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('new/', views.product_detail, name='product_create'),
    path('<int:pk>/', views.product_detail, name='product_detail'),
    path('toggle-visibility/<int:pk>/', views.toggle_product_visibility, name='toggle_visibility'),
    path('delete-image/<int:img_id>/', views.delete_product_image, name='delete_image'),
]
