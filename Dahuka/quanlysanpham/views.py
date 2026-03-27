from django.shortcuts import render

def danhsachsanpham(request):
    return render(request, 'quanlysanpham/danhsachsanpham.html')

def chitietsanpham(request, sanpham_id):
    return render(request, 'quanlysanpham/chitietsanpham.html', {'sanpham_id': sanpham_id})