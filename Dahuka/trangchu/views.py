from django.shortcuts import render

def index(request):
    return render(request, 'base.html')


def xem_san_pham(request):
    return render(request, 'XemSanPham.html')


def chi_tiet_san_pham(request):
    return render(request, 'CTSP.html')


def so_sanh_san_pham(request):
    return render(request, 'SoSanhSanPham.html')


def chi_tiet_khuyen_mai(request):
    return render(request, 'chitietkhuyenmai.html')


def frame_chon_san_pham(request):
    return render(request, 'framechonsanpham.html')


def cong_viec_lap_dat(request):
    return render(request, 'congvieclapdat.html')


def chi_tiet_lap_dat(request):
    return render(request, 'chitietlapdat.html')
