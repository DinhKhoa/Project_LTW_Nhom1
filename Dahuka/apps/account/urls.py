from django.urls import path
from . import views, api_views


urlpatterns = [
    path("dashboard/", views.account_dashboard, name="account_dashboard"),
    path("profile/", views.profile_view, name="profile_view"),
    path("change-password/", views.change_password, name="change_password"),
    path("public-change-password/", views.public_change_password, name="public_change_password"),
    path("addresses/", views.address_list, name="address_list"),
    path("addresses/add/", views.add_address, name="add_address"),
    path("addresses/<int:pk>/edit/", views.edit_address, name="edit_address"),
    path("addresses/<int:pk>/delete/", views.delete_address, name="delete_address"),
    path("purchases/", views.purchase_list, name="purchase_list"),
    path("purchases/<int:pk>/", views.purchase_detail, name="purchase_detail"),
    path("purchases/<int:pk>/cancel/", views.cancel_order, name="cancel_order"),
    # API endpoints
    path("api/profile/", api_views.api_profile, name="api_profile"),
    path(
        "api/change-password/",
        api_views.api_change_password,
        name="api_change_password",
    ),
    path("api/addresses/", api_views.api_addresses, name="api_addresses"),
    path("api/addresses/<int:pk>/", api_views.api_addresses, name="api_address_detail"),
    path("api/orders/", api_views.api_orders, name="api_orders"),
    path("api/orders/<int:pk>/", api_views.api_orders, name="api_order_detail"),
    path("signin/", views.signin, name="signin"),
]
