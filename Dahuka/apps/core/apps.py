from django.apps import AppConfig

# Cấu hình định danh cho ứng dụng Core
class TrangchuConfig(AppConfig):
    """
    Khai báo tên và đường dẫn của app để Django có thể nhận diện
    và tải các thành phần (Models, Signals, Templates) của app này.
    """
    name = 'apps.core'
    verbose_name = 'Hệ thống cốt lõi'
