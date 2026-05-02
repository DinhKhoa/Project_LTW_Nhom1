from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib import messages

from apps.core.utils import get_paginated_data
from apps.core.decorators import staff_required
from apps.orders.services import OrderService
from .selectors import get_assigned_tasks_queryset, get_task_counts, get_task_detail

@login_required
@staff_required
def task_list(request: HttpRequest) -> HttpResponse:
    orders_qs = get_assigned_tasks_queryset(request.user)
    counts = get_task_counts(request.user)
    
    page_obj = get_paginated_data(orders_qs, request, 10)

    return render(request, "task_list.html", {
        "tasks": page_obj,
        "page_obj": page_obj,
        **counts
    })

@login_required
@staff_required
def task_detail(request: HttpRequest, pk: int) -> HttpResponse:
    order = get_task_detail(pk, request.user)

    if request.method == "POST":
        action = request.POST.get("action", "")
        cancel_reason = request.POST.get("cancel_reason", "")
        proof_image = request.FILES.get("proof_image")

        OrderService.handle_order_action(
            order, 
            action, 
            staff_id="", 
            cancel_reason=cancel_reason, 
            proof_image=proof_image, 
            user=request.user
        )
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
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
