from django import forms

class CustomerInfoForm(forms.Form):
    ADDRESS_TYPE_CHOICES = [
        ("home", "Nhà riêng/ Chung cư"),
        ("office", "Cơ quan/ Công ty"),
    ]

    full_name = forms.CharField(
        max_length=100,
        label="Họ tên",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Nhập họ tên"}
        ),
    )
    phone = forms.CharField(
        max_length=15,
        label="Số điện thoại",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Nhập số điện thoại"}
        ),
    )
    province = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    district = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    ward = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    address_detail = forms.CharField(
        label="Địa chỉ",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Nhập địa chỉ chi tiết",
            }
        ),
    )
    address_type = forms.ChoiceField(
        choices=ADDRESS_TYPE_CHOICES,
        initial="home",
        widget=forms.RadioSelect(),
    )
    is_default = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(),
    )
