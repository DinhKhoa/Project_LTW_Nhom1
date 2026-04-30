from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class RegistrationForm(forms.Form):
    last_name = forms.CharField(
        max_length=50, widget=forms.TextInput(attrs={"placeholder": "Họ"})
    )
    first_name = forms.CharField(
        max_length=50, widget=forms.TextInput(attrs={"placeholder": "Tên"})
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={"placeholder": "Ví dụ: 0987654321"}),
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={"placeholder": "example@gmail.com"}),
    )
    birthday = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"type": "date"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Tối thiểu 6 ký tự"})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Nhập lại mật khẩu"})
    )

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if User.objects.filter(username=phone).exists():
            raise ValidationError("Số điện thoại này đã được đăng ký")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Mật khẩu xác nhận không khớp")

        if password and len(password) < 6:
            raise ValidationError("Mật khẩu phải có ít nhất 6 ký tự")

        return cleaned_data


class PublicPasswordChangeForm(forms.Form):
    phone = forms.CharField(
        max_length=20,
        label="Số điện thoại",
        widget=forms.TextInput(attrs={"placeholder": "Nhập số điện thoại của bạn"}),
    )
    current_password = forms.CharField(
        label="Mật khẩu hiện tại",
        widget=forms.PasswordInput(attrs={"placeholder": "Nhập mật khẩu hiện tại"}),
    )
    new_password = forms.CharField(
        label="Mật khẩu mới",
        widget=forms.PasswordInput(attrs={"placeholder": "Nhập mật khẩu mới"}),
    )
    confirm_password = forms.CharField(
        label="Xác nhận mật khẩu mới",
        widget=forms.PasswordInput(attrs={"placeholder": "Nhập lại mật khẩu mới"}),
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            raise ValidationError("Mật khẩu xác nhận không khớp")

        if new_password and len(new_password) < 6:
            raise ValidationError("Mật khẩu mới phải có ít nhất 6 ký tự")

        return cleaned_data
