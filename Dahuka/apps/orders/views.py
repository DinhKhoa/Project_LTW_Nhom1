from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Order
from .services import OrderService


@login_required
def order_list(request):
    query = request.GET.get('q', '')
    trang_thai_filter = request.GET.get('trang_thai', '')
    page_number = request.GET.get('page', 1)

    page_obj = OrderService.get_orders(query, trang_thai_filter, page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'trang_thai_filter': trang_thai_filter,
        'trang_thai_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'orders/order_list.html', context)


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    items = order.items.all()

    if request.method == 'POST':
        action = request.POST.get('action', '')
        staff_id = request.POST.get('assigned_staff', '')
        
        OrderService.handle_order_action(order, action, staff_id)

        return redirect('orders:order_detail', pk=pk)

    current_step = OrderService.calc_current_step(order)

    context = {
        'don_hang': order,
        'chi_tiet_items': items,
        'current_step': current_step,
    }
    return render(request, 'orders/detail.html', context)
