from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Promotion
from django.contrib.auth.models import User
from apps.core.services import CoreService


@receiver(post_save, sender=Promotion)
def notify_new_promotion(sender, instance, created, **kwargs):
    if created and instance.is_active:
        val_display = (
            int(instance.value)
            if instance.value == int(instance.value)
            else instance.value
        )

        if instance.discount_type == "percent":
            discount_str = f"{val_display}%"
        else:
            discount_str = f"{int(instance.value):,}đ".replace(",", ".")

        start_str = instance.start_date.strftime("%d/%m/%Y")
        end_str = instance.end_date.strftime("%d/%m/%Y")

        cond_str = instance.condition
        try:
            val_cond = float(cond_str.replace(".", "").replace(",", ""))
            cond_str = f"{int(val_cond):,}đ".replace(",", ".")
        except (ValueError, TypeError, AttributeError):
            pass

        message = (
            f"Dahuka đang có chương trình khuyến mãi {instance.name} "
            f"giảm {discount_str} cho các đơn hàng có giá trị trên {cond_str} "
            f"áp dụng khi mua tất cả sản phẩm, "
            f"có thời gian từ {start_str} đến {end_str}"
        )

        title = "Chương trình khuyến mãi mới!"
        link = "/"

        users = User.objects.filter(is_active=True, is_staff=False, is_superuser=False)
        for user in users:
            CoreService.create_notification(
                recipient=user, title=title, message=message, link=link
            )
