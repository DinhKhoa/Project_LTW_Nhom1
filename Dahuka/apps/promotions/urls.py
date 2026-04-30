from django.urls import path
from . import views

app_name = 'promotions'

urlpatterns = [
    path('', views.promotion_list, name='promotion_list'),
    path('detail/<int:pk>/', views.promotion_detail, name='promotion_detail'),
    path('add/', views.add_promotion, name='add_promotion'),
    path('edit/<int:pk>/', views.add_promotion, name='edit_promotion'),
    path('delete/<int:pk>/', views.delete_promotion, name='delete_promotion'),
    path('api/detail/<int:pk>/', views.api_promotion_detail, name='api_promotion_detail'),
]