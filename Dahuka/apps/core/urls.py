from django.urls import path
from . import views
from . import api_views

app_name = 'core'

urlpatterns = [
    # --- CÁC TRANG GIAO DIỆN CHÍNH (PAGES) ---
    path('', views.index, name='home'), # Trang chủ
    path('catalog/', views.product_catalog, name='product_catalog'), # Danh mục sản phẩm
    path('product/<slug:slug>/', views.view_product_detail, name='view_product_detail'), # Chi tiết sản phẩm
    path('comparison/', views.product_comparison, name='product_comparison'), # So sánh sản phẩm

    # --- CÁC TRANG QUẢN TRỊ & ĐIỀU HƯỚNG ---
    path('update-home-settings/', views.update_home_settings, name='update_home_settings'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'), # Dashboard tổng quan Admin
    path('login-success/', views.login_success, name='login_success'), # Điều hướng sau đăng nhập

    # --- CÁC ĐƯỜNG DẪN API (TRẢ VỀ JSON) ---
    path('api/notifications/', api_views.fetch_notifications, name='api_fetch_notifications'),
    path('api/notifications/<int:notif_id>/read/', api_views.mark_notification_read, name='api_mark_notification_read'),
    path('api/notifications/read-all/', api_views.mark_all_notifications_read, name='api_mark_all_notifications_read'),
    path('api/search-suggestions/', api_views.api_product_suggestions, name='api_search_suggestions'),
]
