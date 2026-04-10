from django.shortcuts import render


def index(request):
    return render(request, 'core/trangchu.html')


def xem_san_pham(request):
    return render(request, 'core/xem_san_pham.html')


def chi_tiet_san_pham(request):
    return render(request, 'core/chi_tiet_san_pham.html')


def so_sanh_san_pham(request):
    return render(request, 'core/so_sanh_san_pham.html')


def frame_chon_san_pham(request):
    return render(request, 'core/frame_chon_san_pham.html')
