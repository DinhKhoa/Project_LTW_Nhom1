from .models import HomePageSettings, Notification

# --- SERVICE LAYER: NƠI XỬ LÝ LOGIC NGHIỆP VỤ ---
# Quy tắc: Views chỉ gọi Service, không trực tiếp xử lý dữ liệu phức tạp.

class CoreService:
    @staticmethod
    def update_home_page_settings(banner_image=None, dahuka_pro_image=None, dahuka_pro_title=None, dahuka_pro_desc=None):
        """Cập nhật các thông tin cấu hình trang chủ (Dành cho Admin)."""
        settings = HomePageSettings.objects.first()
        if not settings:
            # Nếu chưa có cấu hình nào thì tạo mới một bản ghi đầu tiên
            settings = HomePageSettings.objects.create()

        if banner_image:
            settings.banner_image = banner_image
        if dahuka_pro_image:
            settings.dahuka_pro_image = dahuka_pro_image
        if dahuka_pro_title is not None:
            settings.dahuka_pro_title = dahuka_pro_title
        if dahuka_pro_desc is not None:
            settings.dahuka_pro_desc = dahuka_pro_desc

        settings.save()
        return settings

    @staticmethod
    def create_notification(recipient, title, message, link=None):
        """Tạo một thông báo mới gửi đến người dùng cụ thể trong hệ thống."""
        return Notification.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            link=link
        )
