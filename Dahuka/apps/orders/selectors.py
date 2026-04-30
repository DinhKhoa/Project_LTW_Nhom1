from typing import Optional
from django.core.paginator import Page, Paginator
from django.db.models import Q, QuerySet
from django.contrib.auth.models import User
from apps.core.constants import DEFAULT_PAGE_SIZE
from .models import Order

def get_orders_queryset(
    query: str = "",
    status_filter: str = "",
    user: Optional[User] = None
) -> QuerySet[Order]:
    """
    Selects and filters orders based on query and status.
    """
    orders = Order.objects.all()

    if user and not user.is_staff:
        orders = orders.filter(customer=user)

    if query:
        orders = orders.filter(
            Q(id__icontains=query)
            | Q(full_name__icontains=query)
            | Q(phone__icontains=query)
        )

    if status_filter:
        orders = orders.filter(status=status_filter)

    return orders.prefetch_related('items__product').order_by("-created_at", "-id")

def get_paginated_orders(
    query: str = "",
    status_filter: str = "",
    page_number: int = 1,
    per_page: Optional[int] = None,
    user: Optional[User] = None
) -> Page:
    """
    Retrieves a paginated list of orders.
    """
    if per_page is None:
        per_page = DEFAULT_PAGE_SIZE
        
    orders = get_orders_queryset(query, status_filter, user)
    paginator = Paginator(orders, per_page)
    return paginator.get_page(page_number)
