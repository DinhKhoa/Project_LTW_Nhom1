from django import forms
from .models import Promotion
from apps.products.models import Product

class PromotionForm(forms.ModelForm):
    class Meta:
        model = Promotion
        fields = [
            'name', 'code', 'condition', 'discount_type', 
            'value', 'start_date', 'end_date', 'products', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'VD: Khuyến mãi Tết Nguyên Đán 2026'}),
            'code': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'HERUCR026'}),
            'condition': forms.Textarea(attrs={'class': 'input-field', 'rows': 3, 'placeholder': 'Điều kiện áp dụng...'}),
            'discount_type': forms.Select(attrs={'class': 'input-field'}),
            'value': forms.NumberInput(attrs={'class': 'input-field', 'placeholder': '10'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'input-field'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'input-field'}),
            'products': forms.CheckboxSelectMultiple(),
        }
