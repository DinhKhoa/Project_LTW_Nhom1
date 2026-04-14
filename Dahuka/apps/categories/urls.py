from django.urls import path
from . import views

app_name = 'categories'

urlpatterns = [
    path('', views.category_list, name='category_list'),
    path('add/', views.category_add, name='category_add'),
    path('edit/<int:pk>/', views.category_edit, name='category_edit'),
    path('delete/<int:pk>/', views.category_delete, name='category_delete'),
    path('products/<int:pk>/', views.products_by_category, name='products_by_category'),
]
