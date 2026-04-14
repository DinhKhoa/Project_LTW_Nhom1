from django.shortcuts import render
from django.shortcuts import render, redirect
from .forms import formChiTietKhuyenMai


def chi_tiet_khuyen_mai(request):
    return render(request, 'promotions/chi_tiet_khuyen_mai.html')

def danh_sach_khuyen_mai(request):
    return render(request, 'promotions/quan_ly_khuyen_mai.html')





def them_khuyen_mai(request):
    if request.method == "POST":
        form = formChiTietKhuyenMai(request.POST)
        if form.is_valid():
            # Lấy dữ liệu từ form.cleaned_data
            ten = form.cleaned_data['ten_khuyen_mai']
            ma = form.cleaned_data['ma_khuyen_mai']
            tong_don = form.cleaned_data['tong_don']
            hinh_thuc = form.cleaned_data['hinh_thuc']
            gia_tri = form.cleaned_data['gia_tri']
            ngay_bd = form.cleaned_data['ngay_bat_dau']
            ngay_kt = form.cleaned_data['ngay_ket_thuc']
            san_pham = form.cleaned_data['san_pham_ap_dung']

            # TODO: xử lý lưu vào database hoặc logic khác
            return redirect("core:trangchu")  # sau khi lưu thành công
    else:
        form = formChiTietKhuyenMai()
    return render(request, "promotions/them_khuyen_mai.html", {"form": form})
