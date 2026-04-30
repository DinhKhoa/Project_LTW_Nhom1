from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from apps.promotions.models import Promotion
from apps.core.services import CoreService

class Command(BaseCommand):
    help = 'Quét và gửi thông báo cho các chương trình khuyến mãi vừa bắt đầu'

    def handle(self, *args, **options):
        today = timezone.localtime().date()
        
        # Tìm các khuyến mãi:
        # 1. Đang hoạt động (is_active=True)
        # 2. Đã đến ngày bắt đầu (start_date <= today)
        # 3. Chưa đến ngày kết thúc (end_date >= today)
        # 4. QUAN TRỌNG: Chưa gửi thông báo (notification_sent=False)
        promos_to_notify = Promotion.objects.filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today,
            notification_sent=False
        )

        if not promos_to_notify.exists():
            self.stdout.write(self.style.SUCCESS('Không có khuyến mãi mới cần thông báo.'))
            return

        customers = User.objects.filter(is_superuser=False, is_staff=False)
        
        for promo in promos_to_notify:
            self.stdout.write(f"Đang gửi thông báo cho chương trình: {promo.name}")
            
            for customer in customers:
                CoreService.create_notification(
                    recipient=customer,
                    title="Khuyến mãi đang diễn ra!",
                    message=f"Chương trình '{promo.name}' đã chính thức bắt đầu. Đừng bỏ lỡ cơ hội ưu đãi này!",
                    link=reverse('promotions:promotion_detail', args=[promo.id])
                )
            
            # Đánh dấu đã gửi để lần sau không quét lại
            promo.notification_sent = True
            promo.save()
            
            self.stdout.write(self.style.SUCCESS(f"Đã gửi thông báo thành công cho '{promo.name}'"))
