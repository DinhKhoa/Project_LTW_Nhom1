from django.apps import AppConfig


# ==============================================================================
# CẤU HÌNH ỨNG DỤNG (Application Configuration)
# ==============================================================================
class CategoriesConfig(AppConfig):
    """
    Cấu hình chính cho ứng dụng 'categories' (Danh mục sản phẩm).
    Lớp này giúp Django định danh và nạp các thành phần (Models, Admin, Signals...)
    của app này vào hệ thống chung của dự án Dahuka.
    """
    
    # 1. Đường dẫn vật lý của thư mục ứng dụng trong project
    name = 'apps.categories'
    
    # 2. Tên hiển thị thân thiện của App trong trang quản trị hệ thống
    verbose_name = 'Quản lý Danh mục'
