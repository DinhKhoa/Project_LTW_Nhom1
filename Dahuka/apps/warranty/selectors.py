from typing import Optional
from django.db.models import QuerySet, Q
from .models import WarrantyPageSettings
from apps.orders.models import Order

def get_warranty_settings() -> WarrantyPageSettings:
    """
    Retrieves the global warranty page settings or creates them if they don't exist.
    """
    settings = WarrantyPageSettings.objects.first()
    if not settings:
        settings = WarrantyPageSettings.objects.create()
    return settings

def search_warranty_orders(query: str) -> Optional[QuerySet]:
    """
    Searches for completed orders by order code or phone number.
    """
    if not query:
        return None
        
    return Order.objects.filter(
        Q(order_code__iexact=query) | Q(phone=query)
    ).filter(status='completed').prefetch_related('items__product')
