from django.urls import path
from . import views

app_name = 'promotions'

urlpatterns = [
    path('', views.promotion_list, name='promotion_list'),
    path('detail/', views.promotion_detail, name='promotion_detail'),
    path('add/', views.add_promotion, name='add_promotion'),
]