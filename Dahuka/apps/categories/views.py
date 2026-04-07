from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import DanhMuc
from .services import DanhMucService


def danh_sach_danh_muc(request):
    query = request.GET.get('q', '')
    page_number = request.GET.get('page', 1)
    
    page_obj = DanhMucService.get_danh_mucs(query, page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'categories/danh_sach.html', context)


def them_danh_muc(request):
    if request.method == 'POST':
        ma_danh_muc = request.POST.get('ma_danh_muc', '').strip()
        ten_danh_muc = request.POST.get('ten_danh_muc', '').strip()

        success, _, errors = DanhMucService.validate_and_create(ma_danh_muc, ten_danh_muc)

        if not success:
            return render(request, 'categories/them_danh_muc.html', {
                'errors': errors,
                'ma_danh_muc': ma_danh_muc,
                'ten_danh_muc': ten_danh_muc,
            })

        return redirect('categories:danh_sach')

    return render(request, 'categories/them_danh_muc.html')


def sua_danh_muc(request, pk):
    danh_muc = get_object_or_404(DanhMuc, pk=pk)

    if request.method == 'POST':
        ten_danh_muc = request.POST.get('ten_danh_muc', '').strip()
        ma_danh_muc = request.POST.get('ma_danh_muc', '').strip()

        success, _, errors = DanhMucService.validate_and_update(pk, ma_danh_muc, ten_danh_muc)

        if not success:
            return render(request, 'categories/sua_danh_muc.html', {
                'danh_muc': danh_muc,
                'errors': errors,
            })

        return redirect('categories:danh_sach')

    return render(request, 'categories/sua_danh_muc.html', {'danh_muc': danh_muc})


def xoa_danh_muc(request, pk):
    danh_muc = get_object_or_404(DanhMuc, pk=pk)
    if request.method == 'POST':
        danh_muc.delete()
        return redirect('categories:danh_sach')
    return render(request, 'categories/xoa_danh_muc.html', {'danh_muc': danh_muc})


def chi_tiet_san_pham_theo_danh_muc(request, pk):
    """API endpoint trả về danh sách sản phẩm theo danh mục (cho dropdown)"""
    danh_muc = get_object_or_404(DanhMuc, pk=pk)
    query_ma = request.GET.get('ma', '')

    products = DanhMucService.format_products_for_dropdown(danh_muc, query_ma)

    return JsonResponse({'products': products, 'danh_muc': danh_muc.ten_danh_muc})
