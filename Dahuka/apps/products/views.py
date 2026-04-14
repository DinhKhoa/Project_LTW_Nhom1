from django.shortcuts import render, get_object_or_404
from .models import Product
from apps.categories.models import Category
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

def product_list(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', 'all')
    inventory_filter = request.GET.get('inventory', 'default')

    products_list = Product.objects.all()

    if query:
        products_list = products_list.filter(name__icontains=query) | products_list.filter(sku__icontains=query)
    
    if category_id != 'all':
        products_list = products_list.filter(category_id=category_id)

    if inventory_filter == 'low-to-high':
        products_list = products_list.order_by('stock')
    elif inventory_filter == 'high-to-low':
        products_list = products_list.order_by('-stock')
    else:
        products_list = products_list.order_by('-id')

    # Pagination
    paginator = Paginator(products_list, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'category_id': category_id,
        'inventory_filter': inventory_filter,
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    categories = Category.objects.all()
    context = {
        'product': product,
        'categories': categories,
    }
    return render(request, 'products/product_detail.html', context)

@require_POST
def toggle_product_visibility(request, pk):
    try:
        product = get_object_or_404(Product, pk=pk)
        data = json.loads(request.body)
        product.is_active = data.get('is_visible', True)
        product.save()
        return JsonResponse({'status': 'success', 'is_active': product.is_active})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
