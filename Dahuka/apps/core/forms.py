from django import forms
from apps.account.models import Address, Customer

# --- FORM CẬP NHẬT THÔNG TIN CÁ NHÂN ---
class CustomerForm(forms.ModelForm):
    """Xử lý đồng thời thông tin ở bảng User (Họ tên, Email) và bảng Customer (Giới tính, Ngày sinh, SĐT)."""
    last_name = forms.CharField(max_length=150, required=False, label='Họ', widget=forms.TextInput(attrs={'autocomplete': 'family-name', 'class': 'account-field'}))
    first_name = forms.CharField(max_length=150, required=False, label='Tên', widget=forms.TextInput(attrs={'autocomplete': 'given-name', 'class': 'account-field'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'autocomplete': 'email', 'class': 'account-field'}))

    class Meta:
        model = Customer
        fields = ['gender', 'birthday', 'phone']
        widgets = {
            'phone': forms.TextInput(attrs={'autocomplete': 'tel', 'class': 'account-field'}),
            'birthday': forms.HiddenInput(), # Dùng JS để chọn ngày nên ẩn input gốc
        }

    def save(self, user=None, commit=True):
        """Lưu dữ liệu vào cả 2 bảng User và Customer."""
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

# --- FORM QUẢN LÝ ĐỊA CHỈ ---
class AddressForm(forms.ModelForm):
    """Tạo hoặc chỉnh sửa địa chỉ nhận hàng của người dùng."""
    class Meta:
        model = Address
        fields = ['full_name', 'phone', 'province', 'district', 'ward', 'address_detail', 'address_type', 'is_default']

# --- FORM ĐỔI MẬT KHẨU (YÊU CẦU ĐÃ ĐĂNG NHẬP) ---
class PasswordChangeForm(forms.Form):
    """Kiểm tra mật khẩu cũ và xác nhận mật khẩu mới có khớp nhau hay không."""
    old_password = forms.CharField(widget=forms.PasswordInput, label='Mật khẩu hiện tại')
    new_password = forms.CharField(widget=forms.PasswordInput, label='Mật khẩu mới')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Xác nhận mật khẩu mới')

    def clean(self):
        """Logic kiểm tra xem 2 lần nhập mật khẩu mới có trùng nhau không."""
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        if new_password != confirm_password:
            raise forms.ValidationError("Mật khẩu xác nhận không khớp")
        return cleaned_data

# --- FORM HỦY ĐƠN HÀNG ---
class CancelOrderForm(forms.Form):
    """Yêu cầu người dùng nhập lý do khi muốn hủy đơn hàng."""
    cancel_reason = forms.CharField(widget=forms.Textarea, label='Lý do hủy đơn', required=True)
