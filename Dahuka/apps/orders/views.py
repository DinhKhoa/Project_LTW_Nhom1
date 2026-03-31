from django.shortcuts import render, get_object_or_404, redirect
from .models import DonDatHang
from .services import OrderService


def danh_sach_don_hang(request):
    query = request.GET.get('q', '')
    trang_thai_filter = request.GET.get('trang_thai', '')
    page_number = request.GET.get('page', 1)

    page_obj = OrderService.get_don_hangs(query, trang_thai_filter, page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'trang_thai_filter': trang_thai_filter,
        'trang_thai_choices': DonDatHang.TRANG_THAI_CHOICES,
    }
    return render(request, 'orders/danh_sach.html', context)


def chi_tiet_don_hang(request, pk):
    don_hang = get_object_or_404(DonDatHang, pk=pk)
    chi_tiet_items = don_hang.chitietdonhang_set.all()

    if request.method == 'POST':
        action = request.POST.get('action', '')
        nhan_vien = request.POST.get('nhan_vien_phu_trach', '')
        
        OrderService.handle_order_action(don_hang, action, nhan_vien)

        return redirect('orders:chi_tiet', pk=pk)

    current_step = OrderService.calc_current_step(don_hang)

    context = {
        'don_hang': don_hang,
        'chi_tiet_items': chi_tiet_items,
        'current_step': current_step,
    }
    return render(request, 'orders/chi_tiet.html', context)
