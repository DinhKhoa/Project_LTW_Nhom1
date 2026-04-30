from typing import Any
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from apps.core.decorators import admin_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Prefetch
from django.http import Http404, HttpRequest, HttpResponse

from .models import Order, OrderItem
from .services import OrderService
from . import selectors


@login_required
@admin_required
def order_list(request: HttpRequest) -> HttpResponse:
    """
    View to list orders with filtering and pagination.
    """
    query = request.GET.get("q", "")
    trang_thai_filter = request.GET.get("trang_thai", "")
    page_number = int(request.GET.get("page", 1))

    # Fetch paginated orders via selector
    page_obj = selectors.get_paginated_orders(
        query=query, 
        status_filter=trang_thai_filter, 
        page_number=page_number, 
        user=request.user
    )

    # Summary statistics for admin
    total_count = Order.objects.count()
    pending_count = Order.objects.filter(status='pending').count()
    confirmed_count = Order.objects.filter(status='confirmed').count()
    processing_count = Order.objects.filter(status='processing').count()
    completed_count = Order.objects.filter(status='completed').count()
    cancelled_count = Order.objects.filter(status='cancelled').count()

    context = {
        "page_obj": page_obj,
        "query": query,
        "trang_thai_filter": trang_thai_filter,
        "trang_thai_choices": Order.STATUS_CHOICES,
        "total_count": total_count,
        "pending_count": pending_count,
        "confirmed_count": confirmed_count,
        "processing_count": processing_count,
        "completed_count": completed_count,
        "cancelled_count": cancelled_count,
    }
    return render(request, "order_list.html", context)


@login_required
@admin_required
def order_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """
    View to display order details and handle staff actions.
    """
    # Use pre-fetch logic to optimize queries
    items_qs = OrderItem.objects.select_related('product').all()
    order = get_object_or_404(
        Order.objects.select_related('customer', 'assigned_staff').prefetch_related(
            Prefetch('items', queryset=items_qs)
        ),
        pk=pk
    )
    
    # Permission check: Only owner or staff can view
    if not request.user.is_staff and order.customer != request.user:
        raise Http404("Bạn không có quyền xem đơn hàng này.")

    if request.method == "POST":
        # Only staff can update order status or assign staff
        if not request.user.is_staff:
            messages.error(request, "Bạn không có quyền thực hiện thao tác này.")
            return redirect("orders:order_detail", pk=pk)

        action = request.POST.get("action", "")
        staff_id = request.POST.get("assigned_staff", "")
        cancel_reason = request.POST.get("cancel_reason", "")
        proof_image = request.FILES.get("proof_image")

        OrderService.handle_order_action(order, action, staff_id, cancel_reason, proof_image, user=request.user)
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({
                "status": "success",
                "message": "Cập nhật đơn hàng thành công.",
                "order_status": order.get_status_display(),
                "order_status_raw": order.status,
                "current_step": OrderService.calc_current_step(order),
            })

        messages.success(request, "Cập nhật đơn hàng thành công.")
        return redirect("orders:order_detail", pk=pk)

    view_type = "customer"
    if request.user.is_superuser:
        view_type = "admin"
    elif request.user == order.assigned_staff:
        view_type = "staff"

    context = {
        "order": order,
        "items": order.items.all(),
        "current_step": OrderService.calc_current_step(order),
        "staff_list": User.objects.filter(is_staff=True, is_superuser=False).select_related('customer'),
        "view_type": view_type,
    }
    return render(request, "order_detail.html", context)
