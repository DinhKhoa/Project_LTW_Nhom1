from django import forms


class CustomerInfoForm(forms.Form):
    CITY_CHOICES = [
        ("Đà Nẵng", "Đà Nẵng"),
        ("Hà Nội", "Hà Nội"),
        ("Hồ Chí Minh", "Hồ Chí Minh"),
        ("Hải Phòng", "Hải Phòng"),
        ("Cần Thơ", "Cần Thơ"),
    ]

    ADDRESS_TYPE_CHOICES = [
        ("home", "Nhà riêng/ Chung cư"),
        ("office", "Cơ quan/ Công ty"),
    ]

    customer_name = forms.CharField(
        max_length=100,
        label="Họ tên",
        widget=forms.TextInput(
            attrs={"class": "cform-input", "placeholder": "Nhập họ tên"}
        ),
    )
    customer_phone = forms.CharField(
        max_length=15,
        label="Số điện thoại",
        widget=forms.TextInput(
            attrs={"class": "cform-input", "placeholder": "Nhập số điện thoại"}
        ),
    )
    customer_email = forms.EmailField(
        required=False,
        label="Email",
        widget=forms.EmailInput(
            attrs={"class": "cform-input", "placeholder": "Nhập email"}
        ),
    )
    customer_city = forms.ChoiceField(
        choices=CITY_CHOICES,
        initial="Đà Nẵng",
        label="Tỉnh/Thành phố",
        widget=forms.Select(attrs={"class": "cform-input cform-select"}),
    )
    customer_district = forms.CharField(
        max_length=100,
        label="Quận/Huyện",
        widget=forms.TextInput(
            attrs={"class": "cform-input", "placeholder": "Nhập Quận/Huyện"}
        ),
    )
    customer_ward = forms.CharField(
        max_length=100,
        label="Phường/Xã",
        widget=forms.TextInput(
            attrs={"class": "cform-input", "placeholder": "Nhập Phường/Xã"}
        ),
    )
    customer_street = forms.CharField(
        label="Địa chỉ",
        widget=forms.Textarea(
            attrs={
                "class": "cform-input cform-textarea",
                "rows": 4,
                "placeholder": "Nhập địa chỉ chi tiết",
            }
        ),
    )
    address_type = forms.ChoiceField(
        choices=ADDRESS_TYPE_CHOICES,
        initial="home",
        widget=forms.RadioSelect(
            attrs={"class": "d-none"}
        ),  # We will use custom CSS in template
    )
    is_default = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={"class": "d-none"}
        ),  # We will use custom CSS in template
    )
