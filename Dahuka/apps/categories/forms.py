from django import forms
from .models import Category
from django.utils.text import slugify


# ==============================================================================
# FORM: QUẢN LÝ DANH MỤC (CategoryForm)
# ==============================================================================
class CategoryForm(forms.ModelForm):
    """
    Biểu mẫu dùng để thêm mới hoặc cập nhật thông tin Danh mục sản phẩm.
    Sử dụng ModelForm để tự động tạo các ô nhập liệu dựa trên cấu hình Model Category.
    """

    class Meta:
        model = Category

        # 1. Bảo mật: Chỉ liệt kê các trường cho phép người dùng nhập/sửa từ giao diện.
        # TUYỆT ĐỐI KHÔNG dùng '__all__' để tránh lỗ hổng Mass Assignment.
        fields = ["name", "description", "image"]

        # 2. Cấu hình Widgets: Tùy chỉnh giao diện HTML (thêm CSS class, placeholder...)
        # giúp tích hợp tốt với các Framework CSS như Bootstrap hoặc Tailwind.
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nhập tên danh mục",
                    "required": True,
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nhập mô tả ngắn gọn cho danh mục này...",
                    "rows": 3,
                }
            ),
        }

    def clean_name(self):
        """
        Hàm kiểm tra (Validation) riêng cho trường 'name'.
        Đảm bảo tên danh mục không bị trùng lặp trong hệ thống (không phân biệt hoa thường).
        """
        name = self.cleaned_data.get("name")
        instance = self.instance  # Lấy đối tượng hiện tại (trong trường hợp đang sửa)

        # Thực hiện truy vấn tìm kiếm các danh mục có tên trùng khớp (iexact: không phân biệt hoa thường)
        qs = Category.objects.filter(name__iexact=name)

        # Nếu đang ở chế độ CHỈNH SỬA (đã có Primary Key - pk)
        if instance and instance.pk:
            # Loại trừ chính đối tượng đang sửa khỏi danh sách kiểm tra để tránh báo lỗi trùng với chính mình
            qs = qs.exclude(pk=instance.pk)

        if qs.exists():
            # Ném ra lỗi ValidationError: Django sẽ tự động hiển thị thông báo này bên dưới ô nhập liệu
            raise forms.ValidationError(f'Danh mục "{name}" đã tồn tại trên hệ thống.')

        return name

    def save(self, commit=True):
        """
        Ghi đè phương thức lưu Form để can thiệp vào logic xử lý dữ liệu trước khi lưu.
        Mục tiêu: Đảm bảo 'slug' luôn được cập nhật đồng bộ theo 'name' mới nhất.
        """
        # 1. Tạo đối tượng instance từ dữ liệu form nhưng chưa lưu vào DB ngay (commit=False)
        instance = super().save(commit=False)

        # 2. Tự động tạo lại slug từ tên danh mục (Ví dụ: "Máy lọc nước" -> "may-loc-nuoc")
        instance.slug = slugify(instance.name)

        # 3. Nếu tham số commit là True (mặc định), tiến hành thực thi lưu vào Database
        if commit:
            instance.save()

        return instance
