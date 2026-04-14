from django.core.paginator import Paginator
from django.db.models import Q
from .models import Category

class CategoryService:
    @staticmethod
    def get_categories(query='', page_number=1, per_page=10):
        categories = Category.objects.all()
        if query:
            categories = categories.filter(
                Q(slug__icontains=query) | Q(name__icontains=query)
            )
        paginator = Paginator(categories, per_page)
        return paginator.get_page(page_number)

    @staticmethod
    def validate_and_create(name):
        errors = {}
        if not name:
            errors['name'] = 'Vui lòng nhập tên danh mục'

        if not errors:
            category = Category.objects.create(name=name)
            return True, category, errors
        return False, None, errors

    @staticmethod
    def validate_and_update(pk, name):
        errors = {}
        if not name:
            errors['name'] = 'Vui lòng nhập tên danh mục'

        if not errors:
            category = Category.objects.get(pk=pk)
            category.name = name
            category.save()
            return True, category, errors
        return False, None, errors

    @staticmethod
    def format_products_for_dropdown(category, query_sku=''):
        from apps.products.models import Product # Avoid circular
        products_qs = Product.objects.filter(category=category)
        if query_sku:
            products_qs = products_qs.filter(sku__icontains=query_sku)

        products = []
        for p in products_qs:
            # Logic for stock status
            status_type = 'day_du'
            status_display = 'Đầy đủ'
            if p.stock == 0:
                status_type = 'het_hang'
                status_display = 'Hết hàng'
            elif p.stock < 10:
                status_type = 'thap'
                status_display = 'Sắp hết'

            products.append({
                'id': p.id,
                'sku': p.sku,
                'ma_san_pham': p.sku,
                'ten_san_pham': p.name,
                'gia_tien': float(p.price),
                'ton_kho': p.stock,
                'trang_thai_hien_thi': p.is_active,
                'trang_thai_ton_kho': status_type,
                'trang_thai_ton_kho_display': status_display,
                'category': p.category.name,
            })
        return products
