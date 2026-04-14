from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='home'),
    path('catalog/', views.product_list, name='product_catalog'),
    path('product-detail/', views.product_detail, name='product_detail'),
    path('comparison/', views.product_comparison, name='product_comparison'),
    path('selection-frame/', views.product_selection_frame, name='product_selection_frame'),
    path('update-home-settings/', views.update_home_settings, name='update_home_settings'),
    path('login-success/', views.login_success, name='login_success'),
]
