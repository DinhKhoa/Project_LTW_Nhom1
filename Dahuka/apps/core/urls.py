from django.urls import path
from . import views
from . import api_views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='home'),
    path('catalog/', views.product_catalog, name='product_catalog'),
    path('product/<slug:slug>/', views.view_product_detail, name='view_product_detail'),
    path('comparison/', views.product_comparison, name='product_comparison'),

    path('update-home-settings/', views.update_home_settings, name='update_home_settings'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('login-success/', views.login_success, name='login_success'),

    # API Notification
    path('api/notifications/', api_views.fetch_notifications, name='api_fetch_notifications'),
    path('api/notifications/<int:notif_id>/read/', api_views.mark_notification_read, name='api_mark_notification_read'),
    path('api/notifications/read-all/', api_views.mark_all_notifications_read, name='api_mark_all_notifications_read'),
]
