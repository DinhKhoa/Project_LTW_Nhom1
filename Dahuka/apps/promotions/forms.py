from django import forms

class formChiTietKhuyenMai(forms.Form):
    ten_khuyen_mai = forms.CharField(
        label="Tên khuyến mãi",
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'VD: Khuyến mãi Tết Nguyên Đán 2026'})
    )

    ma_khuyen_mai = forms.CharField(
        label="Mã khuyến mãi",
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'HERUCR026'})
    )

    tong_don = forms.IntegerField(
        label="Điều kiện áp dụng (Tổng đơn ≥)",
        min_value=0,
        widget=forms.TextInput(attrs={'class': 'input-field', 'placeholder': '5.000.000'})
    )

    hinh_thuc = forms.ChoiceField(
        label="Hình thức áp dụng",
        choices=[('percent', 'PHẦN TRĂM'), ('fixed', 'CỐ ĐỊNH')],
        widget=forms.Select(attrs={'class': 'input-field'})
    )

    gia_tri = forms.IntegerField(
        label="Giá trị khuyến mãi",
        min_value=0,
        widget=forms.TextInput(attrs={'class': 'input-field', 'placeholder': '10'})
    )

    ngay_bat_dau = forms.DateField(
        label="Ngày bắt đầu",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'input-field'})
    )

    ngay_ket_thuc = forms.DateField(
        label="Ngày kết thúc",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'input-field'})
    )

    # Nếu bạn muốn chọn nhiều sản phẩm áp dụng, có thể thêm:
    san_pham_ap_dung = forms.MultipleChoiceField(
        label="Sản phẩm áp dụng",
        required=False,
        choices=[(f"sp{i}", f"Sản phẩm {i}") for i in range(1, 21)],
        widget=forms.CheckboxSelectMultiple
    )
