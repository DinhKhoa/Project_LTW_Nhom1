from django.urls import path
from . import views

# Nhóm URL cho app products — tiền tố được đặt trong Dahuka/urls.py
app_name = "products"

urlpatterns = [
    path("", views.product_list, name="product_list"),  # Danh sách SP: /products/
    path(
        "new/", views.product_detail, name="product_create"
    ),  # Thêm SP mới: /products/new/
    path(
        "<int:pk>/", views.product_detail, name="product_detail"
    ),  # Sửa SP: /products/1/
    path(
        "toggle-visibility/<int:pk>/",
        views.toggle_product_visibility,
        name="toggle_visibility",
    ),  # Ẩn/hiện SP (AJAX)
    path(
        "delete-image/<int:img_id>/", views.delete_product_image, name="delete_image"
    ),  # Xóa ảnh gallery (AJAX)
]
