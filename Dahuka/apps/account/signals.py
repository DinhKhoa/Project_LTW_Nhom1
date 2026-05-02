from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Customer

@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):
    if created:
        Customer.objects.get_or_create(
            user=instance,
            defaults={'phone': instance.username if instance.username.isdigit() else ''}
        )

@receiver(post_save, sender=User)
def save_customer_profile(sender, instance, **kwargs):
    if hasattr(instance, 'customer'):
        instance.customer.save()
