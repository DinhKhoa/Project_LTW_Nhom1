from django import forms
from .models import Address, Customer

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['full_name', 'phone', 'email', 'province', 'district', 'ward', 'address_detail', 'address_type', 'is_default']

class CancelOrderForm(forms.Form):
    cancel_reason = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Lý do hủy đơn...'}), required=True)

class CustomerForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)
    phone = forms.CharField(max_length=20, required=False)
    
    class Meta:
        model = Customer
        fields = ['phone']

    def save(self, user=None, commit=True):
        customer = super().save(commit=False)
        if user:
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.save()
        if commit:
            customer.save()
        return customer

class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput, label='Mật khẩu cũ')
    new_password = forms.CharField(widget=forms.PasswordInput, label='Mật khẩu mới')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Xác nhận mật khẩu mới')

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Mật khẩu mới không khớp")
        return cleaned_data
