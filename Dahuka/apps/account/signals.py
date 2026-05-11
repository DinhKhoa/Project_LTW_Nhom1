from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Customer

# Signal: Tự động chạy SAU KHI một User được tạo mới
# Mục đích: Đảm bảo mọi User đều có Customer profile đi kèm
@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):
    if created:  # Chỉ chạy khi tạo mới, không chạy khi cập nhật
        Customer.objects.get_or_create(
            user=instance,
            # Nếu username là số (SĐT) thì lưu vào phone, ngược lại để trống
            defaults={'phone': instance.username if instance.username.isdigit() else ''}
        )

# Signal: Đồng bộ lưu Customer mỗi khi User được save
@receiver(post_save, sender=User)
def save_customer_profile(sender, instance, **kwargs):
    if hasattr(instance, 'customer'):
        instance.customer.save()
