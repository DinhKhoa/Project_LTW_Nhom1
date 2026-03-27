from django.shortcuts import render

def danhsachsanpham(request):
    return render(request, 'danhsachsanpham.html')

def chitietsanpham(request, sanpham_id):
    return render(request, 'chitietsanpham.html')
