from typing import Optional
from django.core.paginator import Page, Paginator
from django.db.models import Q, QuerySet
from django.contrib.auth.models import User
from apps.core.constants import DEFAULT_PAGE_SIZE
from .models import Order


def get_orders_queryset(
    query: str = "", status_filter: str = "", user: Optional[User] = None
) -> QuerySet[Order]:
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

    return orders.prefetch_related("items__product").order_by("-created_at", "-id")


def get_paginated_orders(
    query: str = "",
    status_filter: str = "",
    page_number: int = 1,
    per_page: Optional[int] = None,
    user: Optional[User] = None,
) -> Page:
    if per_page is None:
        per_page = DEFAULT_PAGE_SIZE

    orders = get_orders_queryset(query, status_filter, user)
    paginator = Paginator(orders, per_page)
    return paginator.get_page(page_number)


def get_order_statistics() -> dict:
    return {
        "total": Order.objects.count(),
        "pending": Order.objects.filter(status="pending").count(),
        "confirmed": Order.objects.filter(status="confirmed").count(),
        "processing": Order.objects.filter(status="processing").count(),
        "completed": Order.objects.filter(status="completed").count(),
        "cancelled": Order.objects.filter(status="cancelled").count(),
    }


def get_order_detail(pk: int) -> Order:
    from django.db.models import Prefetch
    from .models import OrderItem

    items_qs = OrderItem.objects.select_related("product").all()
    return (
        Order.objects.select_related("customer", "assigned_staff")
        .prefetch_related(Prefetch("items", queryset=items_qs))
        .get(pk=pk)
    )
