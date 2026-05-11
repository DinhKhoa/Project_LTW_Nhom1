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
    # Trả về thông tin bảo hành của các đơn hàng đã hoàn thành và có mã đơn hàng hoặc số điện thoại trùng với query
    return (
        Order.objects.filter(Q(order_code__iexact=query) | Q(phone=query))
        .filter(status="completed")
        .prefetch_related("items__product")
    )
