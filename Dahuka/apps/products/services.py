"""
Services for products module.
Put business logic here to keep views lean.
"""
from .models import Product


class ProductsService:
    @staticmethod
    def format_products_for_dropdown(category, query_sku=''):
        """
        Format products for a category as a dropdown list.
        
        Args:
            category: Category instance
            query_sku: Optional SKU filter string
            
        Returns:
            List of product dictionaries with formatted data
        """
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
                'stock_status': p.stock_status,
                'stock_status_display': p.stock_status_display,
                'category': p.category.name,
            })
        return products
