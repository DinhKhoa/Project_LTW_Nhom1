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

    def clean_name(self):
        name = self.cleaned_data.get('name')
        instance = self.instance
        qs = Promotion.objects.filter(name__iexact=name)
        if instance and instance.pk:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise forms.ValidationError(f'Chương trình khuyến mãi "{name}" đã tồn tại.')
        return name

    def clean_code(self):
        code = self.cleaned_data.get('code')
        instance = self.instance
        qs = Promotion.objects.filter(code__iexact=code)
        if instance and instance.pk:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise forms.ValidationError(f'Mã khuyến mãi "{code}" đã được sử dụng.')
        return code

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Ngày bắt đầu không thể sau ngày kết thúc.")
        return cleaned_data

