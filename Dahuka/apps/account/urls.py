from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.account_dashboard, name="account_dashboard"),
    path("profile/", views.profile_view, name="profile_view"),
    path("change-password/", views.change_password, name="change_password"),
    path("addresses/", views.address_list, name="address_list"),
    path("addresses/add/", views.add_address, name="add_address"),
    path("addresses/<int:pk>/edit/", views.edit_address, name="edit_address"),
    path("addresses/<int:pk>/delete/", views.delete_address, name="delete_address"),
    path("orders/", views.order_list, name="order_list"),
    path("orders/<int:pk>/", views.order_detail, name="order_detail"),
    path("orders/<int:pk>/cancel/", views.cancel_order, name="cancel_order"),
    
    # API endpoints
    path("api/profile/", views.api_profile, name="api_profile"),
    path("api/change-password/", views.api_change_password, name="api_change_password"),
    path("api/addresses/", views.api_addresses, name="api_addresses"),
    path("api/addresses/<int:pk>/", views.api_addresses, name="api_address_detail"),
    path("api/orders/", views.api_orders, name="api_orders"),
    path("api/orders/<int:pk>/", views.api_orders, name="api_order_detail"),
]
