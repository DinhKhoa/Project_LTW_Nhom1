"""
Services for core module.
Put business logic here to keep views lean.
"""

from .models import Notification

class CoreService:
    @staticmethod
    def create_notification(recipient, title, message, link=None):
        """
        Tạo mới một thông báo cho người dùng.
        """
        if not recipient:
            return None
            
        return Notification.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            link=link
        )
