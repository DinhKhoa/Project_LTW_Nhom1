from django.db.models import QuerySet, Prefetch
from apps.orders.models import Order, OrderItem
from django.contrib.auth.models import User

def get_assigned_tasks_queryset(user: User) -> QuerySet:
    """
    Returns a queryset of orders assigned to a specific staff member.
    """
    return Order.objects.filter(assigned_staff=user).order_by("-id")

def get_task_counts(user: User) -> dict:
    """
    Returns counts of tasks in different statuses for a staff member.
    """
    qs = get_assigned_tasks_queryset(user)
    return {
        "completed_count": qs.filter(status="completed").count(),
        "in_progress_count": qs.filter(status="processing").count(),
        "confirmed_count": qs.filter(status="confirmed").count(),
    }

def get_task_detail(pk: int, user: User) -> Order:
    """
    Retrieves detailed order information with prefetched items for a staff member.
    """
    from django.shortcuts import get_object_or_404
    items_qs = OrderItem.objects.select_related('product').all()
    return get_object_or_404(
        Order.objects.prefetch_related(
            Prefetch('items', queryset=items_qs)
        ),
        pk=pk,
        assigned_staff=user
    )
