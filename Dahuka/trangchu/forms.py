from django import forms

from .models import Address, Customer


class CustomerForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Nguyen',
            }
        ),
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Van An',
            }
        ),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'name@example.com',
            }
        ),
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': '0999555666',
            }
        ),
    )

    class Meta:
        model = Customer
        fields = ['phone']

    def save(self, user, commit=True):
        customer = super().save(commit=False)
        customer.user = user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.save()
        if commit:
            customer.save()
        return customer


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            'full_name',
            'phone',
            'email',
            'province',
            'district',
            'ward',
            'address_detail',
            'address_type',
            'is_default',
        ]
        widgets = {
            'full_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': '', 'required': True}
            ),
            'phone': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': '+84', 'required': True}
            ),
            'email': forms.EmailInput(
                attrs={'class': 'form-control', 'placeholder': '', 'required': True}
            ),
            'province': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Vui lòng chọn thành phố', 'required': True}
            ),
            'district': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Vui lòng chọn quận/huyện', 'required': True}
            ),
            'ward': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Vui lòng chọn phường/xã', 'required': True}
            ),
            'address_detail': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Số nhà, tên đường, tòa nhà (nếu có)',
                    'rows': 3,
                    'required': True,
                }
            ),
            'address_type': forms.Select(attrs={'class': 'form-control d-none'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['address_type'].choices = [
            ('home', 'Nhà riêng/ Chung cư'),
            ('office', 'Cơ quan/ Công ty'),
        ]


class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        label='Mật khẩu cũ',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Nhập mật khẩu cũ',
            }
        ),
    )
    new_password = forms.CharField(
        label='Mật khẩu mới',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Nhập mật khẩu mới...',
            }
        ),
    )
    confirm_password = forms.CharField(
        label='Xác thực mật khẩu',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Nhập lại mật khẩu mới...',
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError('Mật khẩu mới không trùng khớp')

        return cleaned_data


class CancelOrderForm(forms.Form):
    cancel_reason = forms.CharField(
        label='Lý do hủy đơn hàng',
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'placeholder': 'Vui lòng cho chúng tôi biết thêm lý do hủy đơn của bạn',
                'rows': 4,
                'required': True,
            }
        ),
    )
