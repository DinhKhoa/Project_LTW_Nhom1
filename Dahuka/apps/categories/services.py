from django.core.paginator import Paginator
from django.db.models import Q
from .models import Category
from apps.core.constants import DEFAULT_PAGE_SIZE

class CategoryService:
    @staticmethod
    def get_categories(query='', page_number=1, per_page=None):
        if per_page is None:
            per_page = DEFAULT_PAGE_SIZE
        categories = Category.objects.all()
        if query:
            categories = categories.filter(
                Q(code__icontains=query) | Q(name__icontains=query) | Q(slug__icontains=query)
            )
        paginator = Paginator(categories, per_page)
        return paginator.get_page(page_number)

    @staticmethod
    def validate_and_create(name):
        errors = {}
        if not name:
            errors['name'] = 'Vui lòng nhập tên danh mục'
        elif Category.objects.filter(name__iexact=name).exists():
            errors['name'] = f'Danh mục "{name}" đã tồn tại'

        if not errors:
            try:
                category = Category.objects.create(name=name)
                return True, category, errors
            except Exception as e:
                errors['name'] = f'Lỗi hệ thống khi tạo danh mục: {str(e)}'
        return False, None, errors

    @staticmethod
    def validate_and_update(pk, name):
        errors = {}
        if not name:
            errors['name'] = 'Vui lòng nhập tên danh mục'
        elif Category.objects.filter(name__iexact=name).exclude(pk=pk).exists():
            errors['name'] = f'Tên danh mục "{name}" đã được sử dụng bởi một danh mục khác'

        if not errors:
            try:
                category = Category.objects.get(pk=pk)
                category.name = name
                # Force re-generating slug if name changed
                from django.utils.text import slugify
                category.slug = slugify(name)
                category.save()
                return True, category, errors
            except Exception as e:
                errors['name'] = f'Lỗi hệ thống khi cập nhật danh mục: {str(e)}'
        return False, None, errors

