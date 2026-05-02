from typing import Any, Optional
from django.db.models import QuerySet
from .models import Customer, Address

def get_customer_for_user(user: Any) -> Optional[Customer]:
    if not user.is_authenticated:
        return None
    return Customer.objects.filter(user=user).first()

def get_addresses_for_customer(customer: Customer) -> QuerySet[Address]:
    return Address.objects.filter(customer=customer).order_by('-is_default', '-updated_at')

def get_address_by_id(customer: Customer, address_id: int) -> Address:
    from django.shortcuts import get_object_or_404
    return get_object_or_404(Address, id=address_id, customer=customer)

def get_filtered_purchases(user: Any, query: str = "", status: str = "") -> QuerySet:
    from django.db.models import Q
    from apps.orders.models import Order
    
    orders = Order.objects.filter(customer=user).select_related(
        "customer", "assigned_staff"
    )

    if query:
        search_filter = (
            Q(full_name__icontains=query)
            | Q(phone__icontains=query)
            | Q(items__product__name__icontains=query)
            | Q(items__product__id__icontains=query)
        )
        if query.isdigit():
            search_filter |= Q(id=query)
        orders = orders.filter(search_filter).distinct()

    if status:
        orders = orders.filter(status=status)

    return orders.order_by("-created_at")
