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
            products.append({
                'id': p.id,
                'sku': p.sku,
                'name': p.name,
                'price': float(p.price),
                'stock': p.stock,
                'is_active': p.is_active,
                'category': p.category.name,
            })
        return products
