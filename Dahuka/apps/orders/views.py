from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Prefetch
from .models import Order, OrderItem
from .services import OrderService


@login_required
def order_list(request):
    query = request.GET.get("q", "")
    trang_thai_filter = request.GET.get("trang_thai", "")
    page_number = request.GET.get("page", 1)

    page_obj = OrderService.get_orders(
        query, trang_thai_filter, page_number, user=request.user
    )

    context = {
        "page_obj": page_obj,
        "query": query,
        "trang_thai_filter": trang_thai_filter,
        "trang_thai_choices": Order.STATUS_CHOICES,
    }
    return render(request, "order_list.html", context)


@login_required
def order_detail(request, pk):
    # Use select_related and prefetch_related to avoid N+1 queries
    items_qs = OrderItem.objects.select_related('product').all()
    order = get_object_or_404(
        Order.objects.select_related('customer', 'assigned_staff').prefetch_related(
            Prefetch('items', queryset=items_qs)
        ),
        pk=pk
    )
    # Permission check: Only owner or staff can view
    if not request.user.is_staff and order.customer != request.user:
        from django.http import Http404

        raise Http404("Bạn không có quyền xem đơn hàng này.")

    items = order.items.all()  # Already prefetched, no additional query

    if request.method == "POST":
        # Only staff can update order status or assign staff
        if not request.user.is_staff:
            messages.error(request, "Bạn không có quyền thực hiện thao tác này.")
            return redirect("orders:order_detail", pk=pk)

        action = request.POST.get("action", "")
        staff_id = request.POST.get("assigned_staff", "")

        OrderService.handle_order_action(order, action, staff_id)
        messages.success(request, "Cập nhật đơn hàng thành công.")
        return redirect("orders:order_detail", pk=pk)

    current_step = OrderService.calc_current_step(order)

    context = {
        "order": order,
        "items": items,
        "current_step": current_step,
        "staff_list": User.objects.filter(is_staff=True),
    }
    return render(request, "order_detail.html", context)
