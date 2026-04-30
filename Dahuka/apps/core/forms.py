from django import forms
from django.contrib.auth.models import User
from apps.account.models import Address, Customer

class CustomerForm(forms.ModelForm):
    last_name = forms.CharField(max_length=150, required=False, label='Họ', widget=forms.TextInput(attrs={'autocomplete': 'family-name', 'class': 'account-field'}))
    first_name = forms.CharField(max_length=150, required=False, label='Tên', widget=forms.TextInput(attrs={'autocomplete': 'given-name', 'class': 'account-field'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'autocomplete': 'email', 'class': 'account-field'}))

    class Meta:
        model = Customer
        fields = ['gender', 'birthday', 'phone']
        widgets = {
            'phone': forms.TextInput(attrs={'autocomplete': 'tel', 'class': 'account-field'}),
            'birthday': forms.HiddenInput(),
        }

    def save(self, user=None, commit=True):
        customer = super().save(commit=False)
        if user:
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.save()
            customer.user = user
        if commit:
            customer.save()
        return customer

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['full_name', 'phone', 'province', 'district', 'ward', 'address_detail', 'address_type', 'is_default']


class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput, label='Mật khẩu hiện tại')
    new_password = forms.CharField(widget=forms.PasswordInput, label='Mật khẩu mới')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Xác nhận mật khẩu mới')

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        if new_password != confirm_password:
            raise forms.ValidationError("Mật khẩu xác nhận không khớp")
        return cleaned_data

class CancelOrderForm(forms.Form):
    cancel_reason = forms.CharField(widget=forms.Textarea, label='Lý do hủy đơn', required=True)
