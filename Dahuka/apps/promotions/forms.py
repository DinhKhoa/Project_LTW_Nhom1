from django import forms
from django.utils import timezone
from .models import Promotion


class PromotionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['is_active'].initial = True
        self.fields['start_date'].initial = timezone.localtime().date()

    class Meta:
        model = Promotion
        fields = [
            'name', 'condition', 'discount_type', 
            'value', 'start_date', 'end_date', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input-field'}),

            'condition': forms.TextInput(attrs={'class': 'input-field'}),
            'discount_type': forms.Select(attrs={'class': 'input-field', 'style': 'display: none;'}),
            'value': forms.TextInput(attrs={'class': 'input-field'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'input-field'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'input-field'}),

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



    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Ngày bắt đầu không thể sau ngày kết thúc.")
        return cleaned_data

