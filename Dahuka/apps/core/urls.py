from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='home'),
    path('catalog/', views.product_catalog, name='product_catalog'),
    path('product/<int:pk>/', views.view_product_detail, name='product_detail'),
    path('comparison/', views.product_comparison, name='product_comparison'),
    path('selection-frame/', views.product_selection_frame, name='product_selection_frame'),
    path('update-home-settings/', views.update_home_settings, name='update_home_settings'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('login-success/', views.login_success, name='login_success'),
]
