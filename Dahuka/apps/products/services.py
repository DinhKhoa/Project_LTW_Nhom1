"""
Services for products module.
Put business logic here to keep views lean.
"""
from typing import Any, Dict, List, Optional
from django.db import transaction
from .models import Product, ProductImage


class ProductsService:
    @staticmethod
    def format_products_for_dropdown(category: Any, query_sku: str = '') -> List[Dict[str, Any]]:
        """
        Format products for a category as a dropdown list.
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

    @staticmethod
    def handle_product_images(product: Product, files: Dict[str, List[Any]]) -> None:
        """
        Saves multiple images for a product based on type.
        """
        image_types_map = {
            'gallery_images': 'gallery',
            'specs_images': 'specs',
            'features_images': 'features',
            'description_images': 'description',
        }

        with transaction.atomic():
            for field_name, img_type in image_types_map.items():
                img_list = files.get(field_name, [])
                for img in img_list:
                    ProductImage.objects.create(
                        product=product, 
                        image_url=img, 
                        image_type=img_type
                    )

    @staticmethod
    def toggle_visibility(product: Product, is_visible: bool) -> bool:
        """
        Updates product visibility status.
        """
        product.is_active = is_visible
        product.save()
        return product.is_active
