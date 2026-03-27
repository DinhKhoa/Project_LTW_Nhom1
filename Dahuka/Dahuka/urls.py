"""
URL configuration for Dahuka project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from trangchu import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="home"),
    path("login/", views.DahukaLoginView.as_view(), name="login"),
    path("logout/", views.DahukaLogoutView.as_view(), name="logout"),
    path("account/", views.account_dashboard, name="account_dashboard"),
    path("account/profile/", views.profile_view, name="profile_view"),
    path("account/change-password/", views.change_password, name="change_password"),
    path("account/addresses/", views.address_list, name="address_list"),
    path("account/addresses/add/", views.add_address, name="add_address"),
    path("account/addresses/<int:pk>/edit/", views.edit_address, name="edit_address"),
    path("account/addresses/<int:pk>/delete/", views.delete_address, name="delete_address"),
    path("account/orders/", views.order_list, name="order_list"),
    path("account/orders/<int:pk>/", views.order_detail, name="order_detail"),
    path("account/orders/<int:pk>/cancel/", views.cancel_order, name="cancel_order"),
    path("api/profile/", views.api_profile, name="api_profile"),
    path("api/change-password/", views.api_change_password, name="api_change_password"),
    path("api/addresses/", views.api_addresses, name="api_addresses"),
    path("api/addresses/<int:pk>/", views.api_addresses, name="api_address_detail"),
    path("api/orders/", views.api_orders, name="api_orders"),
    path("api/orders/<int:pk>/", views.api_orders, name="api_order_detail"),
    path("api/orders/<int:pk>/cancel/", views.api_cancel_order, name="api_cancel_order"),
]
