from django.urls import path
from . import views

# ==============================================================================
# ROUTING: ĐỊNH TUYẾN URL CHO DANH MỤC (URL Configuration)
# ==============================================================================
# Tuyệt đối sử dụng 'app_name' để kích hoạt tính năng Namespacing của Django.
# Điều này giúp bạn gọi URL trong Template một cách chính xác: {% url 'categories:name' %}
# Tránh xung đột nếu các app khác cũng có tên URL trùng nhau (như 'add' hay 'edit').

app_name = "categories"

urlpatterns = [
    # 1. Trang hiển thị danh sách toàn bộ danh mục (Dành cho Admin/Quản lý)
    # Đường dẫn ví dụ: /categories/
    path("", views.category_list, name="category_list"),
    # 2. Trang biểu mẫu để thêm mới một danh mục
    # Đường dẫn ví dụ: /categories/add/
    path("add/", views.category_add, name="category_add"),
    # 3. Trang chỉnh sửa thông tin danh mục dựa trên khóa chính (ID)
    # Đường dẫn ví dụ: /categories/edit/5/
    path("edit/<int:pk>/", views.category_edit, name="category_edit"),
    # 4. Đường dẫn xử lý yêu cầu xóa danh mục
    # Đường dẫn ví dụ: /categories/delete/5/
    path("delete/<int:pk>/", views.category_delete, name="category_delete"),
    # 5. API/View hỗ trợ lấy danh sách sản phẩm thuộc một danh mục cụ thể
    # Thường được sử dụng cho các tính năng lọc sản phẩm bằng AJAX (không tải lại trang).
    path("products/<int:pk>/", views.get_category_products, name="category_products"),
]
