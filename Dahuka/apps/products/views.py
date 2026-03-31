from django.shortcuts import render

def danhsachsanpham(request):
    return render(request, 'products/danhsachsanpham.html')

def chitietsanpham(request, sanpham_id):
    return render(request, 'products/chitietsanpham.html', {'sanpham_id': sanpham_id})