from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "category",
            "name",
            "sku",
            "price",
            "image",
            "stock",
            "short_description",
            "description",
            "spec_power",
            "spec_technology",
            "spec_dimensions",
            "spec_type",
            "spec_capacity",
            "spec_hot_temp",
            "spec_cold_temp",
            "spec_release_year",
            "spec_origin",
            "spec_filters_count",
            "spec_weight",
            "spec_warranty",
            "spec_water_source",
            "spec_features",
            "spec_other",
            "is_active",
            "is_featured",
        ]
        widgets = {
            "category": forms.Select(attrs={"class": "form-control-dahuka"}),
            "name": forms.TextInput(
                attrs={
                    "class": "form-control-dahuka",
                    "placeholder": "Nhập tên sản phẩm",
                }
            ),
            "sku": forms.TextInput(
                attrs={"class": "form-control-dahuka", "placeholder": "VD: MP-S96"}
            ),
            "price": forms.NumberInput(
                attrs={"class": "form-control-dahuka", "placeholder": "Giá bán (VNĐ)"}
            ),
            "stock": forms.NumberInput(
                attrs={
                    "class": "form-control-dahuka",
                    "placeholder": "Số lượng tồn kho",
                }
            ),
            "short_description": forms.Textarea(
                attrs={"class": "form-control-dahuka", "rows": 2}
            ),
            "description": forms.Textarea(
                attrs={"class": "form-control-dahuka", "rows": 5}
            ),
            "spec_power": forms.TextInput(attrs={"class": "form-control-dahuka"}),
            "spec_technology": forms.TextInput(attrs={"class": "form-control-dahuka"}),
            "spec_dimensions": forms.TextInput(attrs={"class": "form-control-dahuka"}),
            "spec_type": forms.TextInput(attrs={"class": "form-control-dahuka"}),
            "spec_capacity": forms.TextInput(attrs={"class": "form-control-dahuka"}),
            "spec_hot_temp": forms.TextInput(
                attrs={"class": "form-control-dahuka"}
            ),
            "spec_cold_temp": forms.TextInput(
                attrs={"class": "form-control-dahuka"}
            ),
            "spec_release_year": forms.TextInput(attrs={"class": "form-control-dahuka"}),
            "spec_origin": forms.TextInput(
                attrs={"class": "form-control-dahuka"}
            ),
            "spec_filters_count": forms.TextInput(attrs={"class": "form-control-dahuka"}),
            "spec_weight": forms.TextInput(attrs={"class": "form-control-dahuka"}),
            "spec_warranty": forms.TextInput(attrs={"class": "form-control-dahuka"}),
            "spec_water_source": forms.TextInput(attrs={"class": "form-control-dahuka"}),
            "spec_features": forms.Textarea(
                attrs={"class": "form-control-dahuka", "rows": 2}
            ),
            "spec_other": forms.Textarea(
                attrs={"class": "form-control-dahuka", "rows": 2}
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "ios-toggle"}),
            "is_featured": forms.CheckboxInput(attrs={"class": "ios-toggle"}),
        }

    def clean_name(self):
        name = self.cleaned_data.get("name")
        instance = self.instance
        qs = Product.objects.filter(name__iexact=name)
        if instance and instance.pk:
            qs = qs.exclude(pk=instance.pk)

        if qs.exists():
            raise forms.ValidationError(f'Sản phẩm với tên "{name}" đã tồn tại.')
        return name

    def clean_sku(self):
        sku = self.cleaned_data.get("sku")
        instance = self.instance
        qs = Product.objects.filter(sku__iexact=sku)
        if instance and instance.pk:
            qs = qs.exclude(pk=instance.pk)

        if qs.exists():
            raise forms.ValidationError(f'Mã SKU "{sku}" đã tồn tại trong hệ thống.')
        return sku
