from typing import Optional
from django.db.models import QuerySet, Q
from .models import Product

def get_filtered_products(
    query: str = "",
    category_id: str = "all",
    inventory_filter: str = "default",
    is_active: Optional[bool] = None
) -> QuerySet[Product]:
    products = Product.objects.select_related('category').all()
    
    if is_active is not None:
        products = products.filter(is_active=is_active)

    if query:
        products = products.filter(
            Q(name__icontains=query)
        )
    
    if category_id != 'all':
        products = products.filter(category_id=category_id)

    if inventory_filter == 'low-to-high':
        products = products.order_by('stock')
    elif inventory_filter == 'high-to-low':
        products = products.order_by('-stock')
    else:
        products = products.order_by('-id')

    return products

def get_product_by_id(pk: int) -> Product:
    from django.shortcuts import get_object_or_404
    return get_object_or_404(Product.objects.select_related('category'), pk=pk)
