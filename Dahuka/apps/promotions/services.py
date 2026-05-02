from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from apps.core.services import CoreService
from .models import Promotion

class PromotionService:
    @staticmethod
    def send_promotion_notifications(promotion: Promotion):
        """
        Gửi thông báo về chương trình khuyến mãi cho tất cả khách hàng.
        """
        today = timezone.localtime().date()
        # Chỉ gửi nếu khuyến mãi đang hoạt động, bắt đầu từ hôm nay/quá khứ và CHƯA GỬI
        if promotion.is_active and promotion.start_date <= today and not promotion.notification_sent:
            customers = User.objects.filter(is_superuser=False, is_staff=False)
            for customer in customers:
                CoreService.create_notification(
                    recipient=customer,
                    title="Khuyến mãi đang diễn ra!",
                    message=f"Chương trình '{promotion.name}' đã chính thức bắt đầu. Đừng bỏ lỡ!",
                    link=reverse('promotions:promotion_detail', args=[promotion.id])
                )
            
            # Đánh dấu đã gửi
            promotion.notification_sent = True
            promotion.save(update_fields=['notification_sent'])
            return True
        return False
