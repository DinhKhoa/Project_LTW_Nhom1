from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from .models import DonDatHang, ChiTietDonHang


def danh_sach_don_hang(request):
    query = request.GET.get('q', '')
    trang_thai_filter = request.GET.get('trang_thai', '')
    don_hangs = DonDatHang.objects.all()

    if query:
        don_hangs = don_hangs.filter(
            Q(ma_don_hang__icontains=query) | Q(ho_ten__icontains=query)
        )

    if trang_thai_filter:
        don_hangs = don_hangs.filter(trang_thai=trang_thai_filter)

    paginator = Paginator(don_hangs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'trang_thai_filter': trang_thai_filter,
        'trang_thai_choices': DonDatHang.TRANG_THAI_CHOICES,
    }
    return render(request, 'quanlydondathang/danh_sach.html', context)


def chi_tiet_don_hang(request, pk):
    don_hang = get_object_or_404(DonDatHang, pk=pk)
    chi_tiet_items = don_hang.chitietdonhang_set.all()

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'xac_nhan':
            don_hang.trang_thai = 'da_xac_nhan'
            don_hang.save()
        elif action == 'dang_giao':
            don_hang.trang_thai = 'dang_giao_hang'
            don_hang.save()
        elif action == 'giao_thanh_cong':
            don_hang.trang_thai = 'giao_hang_thanh_cong'
            don_hang.trang_thai_thanh_toan = 'da_thanh_toan'
            don_hang.save()
        elif action == 'huy_don':
            don_hang.trang_thai = 'da_huy'
            don_hang.save()
        elif action == 'luu_thay_doi':
            nhan_vien = request.POST.get('nhan_vien_phu_trach', '')
            don_hang.nhan_vien_phu_trach = nhan_vien
            don_hang.save()

        return redirect('quanlydondathang:chi_tiet', pk=pk)

    # Determine step index for the progress bar
    trang_thai_steps = ['cho_xac_nhan', 'da_xac_nhan', 'dang_giao_hang', 'giao_hang_thanh_cong']
    current_step = 0
    if don_hang.trang_thai in trang_thai_steps:
        current_step = trang_thai_steps.index(don_hang.trang_thai)

    context = {
        'don_hang': don_hang,
        'chi_tiet_items': chi_tiet_items,
        'current_step': current_step,
    }
    return render(request, 'quanlydondathang/chi_tiet.html', context)
