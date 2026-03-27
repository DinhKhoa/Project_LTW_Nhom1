from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from .models import DanhMuc, SanPham


def danh_sach_danh_muc(request):
    query = request.GET.get('q', '')
    danh_mucs = DanhMuc.objects.all()

    if query:
        danh_mucs = danh_mucs.filter(
            Q(ma_danh_muc__icontains=query) | Q(ten_danh_muc__icontains=query)
        )

    paginator = Paginator(danh_mucs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'quanlydanhmuc/danh_sach.html', context)


def them_danh_muc(request):
    if request.method == 'POST':
        ma_danh_muc = request.POST.get('ma_danh_muc', '').strip()
        ten_danh_muc = request.POST.get('ten_danh_muc', '').strip()

        errors = {}
        if not ma_danh_muc:
            errors['ma_danh_muc'] = 'Vui lòng nhập mã danh mục'
        elif DanhMuc.objects.filter(ma_danh_muc=ma_danh_muc).exists():
            errors['ma_danh_muc'] = 'Mã danh mục đã tồn tại'

        if not ten_danh_muc:
            errors['ten_danh_muc'] = 'Vui lòng nhập tên danh mục'

        if errors:
            return render(request, 'quanlydanhmuc/them_danh_muc.html', {
                'errors': errors,
                'ma_danh_muc': ma_danh_muc,
                'ten_danh_muc': ten_danh_muc,
            })

        DanhMuc.objects.create(ma_danh_muc=ma_danh_muc, ten_danh_muc=ten_danh_muc)
        return redirect('quanlydanhmuc:danh_sach')

    return render(request, 'quanlydanhmuc/them_danh_muc.html')


def sua_danh_muc(request, pk):
    danh_muc = get_object_or_404(DanhMuc, pk=pk)

    if request.method == 'POST':
        ten_danh_muc = request.POST.get('ten_danh_muc', '').strip()
        ma_danh_muc = request.POST.get('ma_danh_muc', '').strip()

        errors = {}
        if not ma_danh_muc:
            errors['ma_danh_muc'] = 'Vui lòng nhập mã danh mục'
        elif DanhMuc.objects.filter(ma_danh_muc=ma_danh_muc).exclude(pk=pk).exists():
            errors['ma_danh_muc'] = 'Mã danh mục đã tồn tại'

        if not ten_danh_muc:
            errors['ten_danh_muc'] = 'Vui lòng nhập tên danh mục'

        if errors:
            return render(request, 'quanlydanhmuc/sua_danh_muc.html', {
                'danh_muc': danh_muc,
                'errors': errors,
            })

        danh_muc.ma_danh_muc = ma_danh_muc
        danh_muc.ten_danh_muc = ten_danh_muc
        danh_muc.save()
        return redirect('quanlydanhmuc:danh_sach')

    return render(request, 'quanlydanhmuc/sua_danh_muc.html', {'danh_muc': danh_muc})


def xoa_danh_muc(request, pk):
    danh_muc = get_object_or_404(DanhMuc, pk=pk)
    if request.method == 'POST':
        danh_muc.delete()
        return redirect('quanlydanhmuc:danh_sach')
    return render(request, 'quanlydanhmuc/xoa_danh_muc.html', {'danh_muc': danh_muc})


def chi_tiet_san_pham_theo_danh_muc(request, pk):
    """API endpoint trả về danh sách sản phẩm theo danh mục (cho dropdown)"""
    danh_muc = get_object_or_404(DanhMuc, pk=pk)
    query_ma = request.GET.get('ma', '')
    filter_dm = request.GET.get('danh_muc', '')

    san_phams = danh_muc.sanpham_set.all()

    if query_ma:
        san_phams = san_phams.filter(ma_san_pham__icontains=query_ma)

    products = []
    for sp in san_phams:
        products.append({
            'ma_san_pham': sp.ma_san_pham,
            'ten_san_pham': sp.ten_san_pham,
            'gia_tien': f"{sp.gia_tien:,.0f}".replace(",", ".") + " đ",
            'ton_kho': sp.ton_kho if sp.ton_kho >= 0 else '∞',
            'trang_thai_ton_kho': sp.trang_thai_ton_kho,
            'trang_thai_ton_kho_display': sp.trang_thai_ton_kho_display,
            'trang_thai_hien_thi': sp.trang_thai_hien_thi,
            'danh_muc': sp.danh_muc.ten_danh_muc,
        })

    return JsonResponse({'products': products, 'danh_muc': danh_muc.ten_danh_muc})
