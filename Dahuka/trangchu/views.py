from django.shortcuts import render

def index(request):
    return render(request, 'trangchu/trangchu.html')


def xem_san_pham(request):
    return render(request, 'trangchu/xem_san_pham.html')


def chi_tiet_san_pham(request):
    return render(request, 'trangchu/chi_tiet_san_pham.html')


def so_sanh_san_pham(request):
    return render(request, 'trangchu/so_sanh_san_pham.html')




def frame_chon_san_pham(request):
    return render(request, 'trangchu/framechonsanpham.html')


def cong_viec_lap_dat(request):
    return render(request, 'congvieclapdat.html')


def chi_tiet_lap_dat(request):
    return render(request, 'chitietlapdat.html')