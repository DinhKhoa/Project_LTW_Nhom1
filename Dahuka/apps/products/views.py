from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from apps.core.utils import get_paginated_data
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Product
from .forms import ProductForm
from apps.categories.models import Category
import json

from apps.core.decorators import staff_required

@login_required
@staff_required
def product_list(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', 'all')
    inventory_filter = request.GET.get('inventory', 'default')

    # Use select_related to avoid N+1 query on category
    products_list = Product.objects.select_related('category').all()

    if query:
        products_list = products_list.filter(name__icontains=query) | products_list.filter(sku__icontains=query)
    
    if category_id != 'all':
        products_list = products_list.filter(category_id=category_id)

    if inventory_filter == 'low-to-high':
        products_list = products_list.order_by('stock')
    elif inventory_filter == 'high-to-low':
        products_list = products_list.order_by('-stock')
    else:
        products_list = products_list.order_by('id')

    # Pagination
    page_obj = get_paginated_data(products_list, request, 10)

    categories = Category.objects.all()

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'category_id': category_id,
        'inventory_filter': inventory_filter,
    }
    return render(request, 'product_list.html', context)

@login_required
@staff_required
def product_detail(request, pk=None):
    if pk:
        product = get_object_or_404(Product, pk=pk)
        mode = 'update'
    else:
        product = None
        mode = 'create'

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            saved_product = form.save()
            
            # Handle additional images by category
            from .models import ProductImage
            image_types_map = {
                'gallery_images': 'gallery',
                'specs_images': 'specs',
                'features_images': 'features',
                'description_images': 'description',
            }

            for field_name, img_type in image_types_map.items():
                files = request.FILES.getlist(field_name)
                for img in files:
                    ProductImage.objects.create(product=saved_product, image_url=img, image_type=img_type)

            messages.success(request, f'Đã {"cập nhật" if pk else "thêm mới"} sản phẩm thành công!')
            return redirect('products:product_detail', pk=saved_product.pk)
        messages.error(request, 'Không thể lưu sản phẩm. Vui lòng kiểm tra lại các trường đã nhập.')
    else:
        form = ProductForm(instance=product)

    images_by_type = {}
    if product:
        from .models import ProductImage
        for itype, _ in ProductImage.IMAGE_TYPES:
            images_by_type[itype] = product.images.filter(image_type=itype)

    categories = Category.objects.all()
    context = {
        'product': product,
        'form': form,
        'categories': categories,
        'mode': mode,
        'images_by_type': images_by_type,
    }
    return render(request, 'product_detail.html', context)


@login_required
@staff_required
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
