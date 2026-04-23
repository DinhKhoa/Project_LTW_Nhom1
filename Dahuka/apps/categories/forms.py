from django import forms
from .models import Category
from django.utils.text import slugify

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập tên danh mục',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập mô tả',
                'rows': 3
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        # Check for unique name (case-insensitive)
        instance = self.instance
        qs = Category.objects.filter(name__iexact=name)
        if instance and instance.pk:
            qs = qs.exclude(pk=instance.pk)
            
        if qs.exists():
            raise forms.ValidationError(f'Danh mục "{name}" đã tồn tại.')
        return name

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Always update slug when name changes for consistency
        instance.slug = slugify(instance.name)
        if commit:
            instance.save()
        return instance
