from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from apps.orders.models import Order, OrderItem
from apps.core.utils import get_paginated_data
from apps.core.decorators import staff_required
from django.contrib import messages


@login_required
@staff_required
def task_list(request):
    """View list of all assigned orders for current staff"""
    orders_query = Order.objects.filter(assigned_staff=request.user).order_by("-id")

    completed_count = orders_query.filter(status="completed").count()
    in_progress_count = orders_query.filter(status="processing").count()
    confirmed_count = orders_query.filter(status="confirmed").count()

    # Use centralized pagination
    page_obj = get_paginated_data(orders_query, request, 10)

    return render(
        request,
        "task_list.html",
        {
            "tasks": page_obj,  # Template expects 'tasks' name
            "page_obj": page_obj,
            "completed_count": completed_count,
            "in_progress_count": in_progress_count,
            "confirmed_count": confirmed_count,
        },
    )


@login_required
@staff_required
def task_detail(request, pk):
    """View details of a specific order for staff update"""
    items_qs = OrderItem.objects.select_related('product').all()
    order = get_object_or_404(
        Order.objects.prefetch_related(
            Prefetch('items', queryset=items_qs)
        ),
        pk=pk,
        assigned_staff=request.user
    )
    if request.method == "POST":
        action = request.POST.get("action", "")
        cancel_reason = request.POST.get("cancel_reason", "")
        proof_image = request.FILES.get("proof_image")

        from apps.orders.services import OrderService
        OrderService.handle_order_action(order, action, staff_id="", cancel_reason=cancel_reason, proof_image=proof_image, user=request.user)
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({
                "status": "success",
                "message": "Cập nhật trạng thái đơn hàng thành công.",
            })

        messages.success(request, "Cập nhật trạng thái đơn hàng thành công.")
        return redirect("tasks:task_detail", pk=pk)
    
    return render(request, "task_detail.html", {
        "order": order,
        "items": order.items.all(),
    })
