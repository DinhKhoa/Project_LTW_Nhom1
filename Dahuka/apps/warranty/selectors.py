from typing import Optional
from django.db.models import QuerySet, Q
from .models import WarrantyPageSettings
from apps.orders.models import Order

def get_warranty_settings() -> WarrantyPageSettings:
    settings = WarrantyPageSettings.objects.first()
    if not settings:
        settings = WarrantyPageSettings.objects.create()
    return settings

def search_warranty_orders(query: str) -> Optional[QuerySet]:
    if not query:
        return None
        
    return Order.objects.filter(
        Q(order_code__iexact=query) | Q(phone=query)
    ).filter(status='completed').prefetch_related('items__product')
