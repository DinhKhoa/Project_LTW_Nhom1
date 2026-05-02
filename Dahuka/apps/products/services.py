from typing import Any, Dict, List
from django.db import transaction
from .models import Product, ProductImage

class ProductsService:
    @staticmethod
    def format_products_for_dropdown(category: Any, query: str = '') -> List[Dict[str, Any]]:
        products_qs = Product.objects.filter(category=category)
        if query:
            products_qs = products_qs.filter(name__icontains=query)

        products = []
        for p in products_qs:
            products.append({
                'id': p.id,
                'name': p.name,
                'price': float(p.price),
                'stock': p.stock,
                'is_active': p.is_active,
                'stock_status': p.stock_status,
                'stock_status_display': p.stock_status_display,
                'category': p.category.name,
            })
        return products

    @staticmethod
    def handle_product_images(product: Product, files: Dict[str, List[Any]]) -> None:
        gallery_images = files.get('gallery_images', [])
        
        with transaction.atomic():
            for img in gallery_images:
                ProductImage.objects.create(
                    product=product, 
                    image_url=img
                )

    @staticmethod
    def toggle_visibility(product: Product, is_visible: bool) -> bool:
        product.is_active = is_visible
        product.save()
        return product.is_active
