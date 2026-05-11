from django import forms
from .models import Product

# Form thêm mới và sửa sản phẩm — dùng trong views.product_detail()
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # Liệt kê rõ từng field để kiểm soát (không dùng '__all__' tránh lỗ hổng bảo mật)
        fields = [
            "category",          # Danh mục thuộc về
            "name",              # Tên sản phẩm
            "price",             # Giá bán
            "image",             # Ảnh chính hiển thị trên danh sách

            "image_features",    # Ảnh tính năng nổi bật
            "image_description", # Ảnh mô tả chi tiết
            "stock",             # Số lượng tồn kho
            "short_description", # Mô tả ngắn (hiển thị trên card sản phẩm)
            "description",       # Mô tả chi tiết đầy đủ
            # Thông số kỹ thuật (spec_*)
            "spec_power", "spec_technology", "spec_dimensions",
            "spec_type", "spec_capacity", "spec_hot_temp",
            "spec_cold_temp", "spec_release_year", "spec_origin",
            "spec_filters_count", "spec_weight",
            "spec_warranty",     # Bảo hành — dùng để tính ngày hết hạn khi đơn hoàn thành
            "spec_water_source", "spec_features", "spec_other",
            "is_active",         # Đang kinh doanh (hiển thị trên website)
            "is_featured",       # Nổi bật (hiển thị ở trang chủ)
        ]
        widgets = {
            "category": forms.Select(attrs={"class": "form-control-dahuka"}),
            "name": forms.TextInput(attrs={"class": "form-control-dahuka", "placeholder": "Nhập tên sản phẩm"}),
            "price": forms.NumberInput(attrs={"class": "form-control-dahuka", "placeholder": "Giá bán (VNĐ)"}),
            # Các input file ẩn — JS sẽ kích hoạt khi admin click vào vùng upload
            "image": forms.FileInput(attrs={"class": "d-none"}),

            "image_features": forms.FileInput(attrs={"class": "d-none"}),
            "image_description": forms.FileInput(attrs={"class": "d-none"}),
            "stock": forms.NumberInput(attrs={"class": "form-control-dahuka", "placeholder": "Số lượng tồn kho"}),
            "short_description": forms.Textarea(attrs={"class": "form-control-dahuka", "rows": 2}),
            "description": forms.Textarea(attrs={"class": "form-control-dahuka", "rows": 5}),
            "spec_power": forms.TextInput(attrs={"class": "form-control-dahuka"}),
            "spec_technology": forms.TextInput(attrs={"class": "form-control-dahuka"}),
            "spec_dimensions": forms.TextInput(attrs={"class": "form-control-dahuka"}),
            "spec_type": forms.TextInput(attrs={"class": "form-control-dahuka"}),
            "spec_capacity": forms.TextInput(attrs={"class": "form-control-dahuka"}),
            "spec_hot_temp": forms.TextInput(attrs={"class": "form-control-dahuka"}),
            "spec_cold_temp": forms.TextInput(attrs={"class": "form-control-dahuka"}),
            "spec_release_year": forms.TextInput(attrs={"class": "form-control-dahuka"}),
            "spec_origin": forms.TextInput(attrs={"class": "form-control-dahuka"}),
            "spec_filters_count": forms.TextInput(attrs={"class": "form-control-dahuka"}),
            "spec_weight": forms.TextInput(attrs={"class": "form-control-dahuka"}),
            "spec_warranty": forms.TextInput(attrs={"class": "form-control-dahuka"}),
            "spec_water_source": forms.TextInput(attrs={"class": "form-control-dahuka"}),
            "spec_features": forms.Textarea(attrs={"class": "form-control-dahuka", "rows": 2}),
            "spec_other": forms.Textarea(attrs={"class": "form-control-dahuka", "rows": 2}),
            # Toggle switch bật/tắt (hiển thị kiểu iOS switch trên giao diện)
            "is_active": forms.CheckboxInput(attrs={"class": "ios-toggle"}),
            "is_featured": forms.CheckboxInput(attrs={"class": "ios-toggle"}),
        }

    def clean_name(self):
        """Kiểm tra tên sản phẩm không bị trùng (không phân biệt hoa thường)."""
        name = self.cleaned_data.get("name")
        instance = self.instance
        qs = Product.objects.filter(name__iexact=name)
        if instance and instance.pk:
            qs = qs.exclude(pk=instance.pk)  # Khi sửa: không đếm chính nó là trùng

        if qs.exists():
            raise forms.ValidationError(f'Sản phẩm với tên "{name}" đã tồn tại.')
        return name
