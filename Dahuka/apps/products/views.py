import json
from typing import Any, Dict
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_POST
from django.contrib import messages

from apps.core.utils import get_paginated_data
from apps.core.decorators import admin_required
from apps.categories.models import Category
from .models import Product, ProductImage
from .forms import ProductForm
from .services import ProductsService
from . import selectors


@login_required
@admin_required
def product_list(request: HttpRequest) -> HttpResponse:
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', 'all')
    inventory_filter = request.GET.get('inventory', 'default')

    products_list = selectors.get_filtered_products(
        query=query,
        category_id=category_id,
        inventory_filter=inventory_filter
    )

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
@admin_required
def product_detail(request: HttpRequest, pk: int = None) -> HttpResponse:
    product = selectors.get_product_by_id(pk) if pk else None
    mode = 'update' if pk else 'create'

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            saved_product = form.save()
            ProductsService.handle_product_images(saved_product, request.FILES)
            messages.success(request, f'Đã {"cập nhật" if pk else "thêm mới"} sản phẩm thành công!')
            return redirect('products:product_detail', pk=saved_product.pk)
        
        messages.error(request, 'Không thể lưu sản phẩm. Vui lòng kiểm tra lại các trường đã nhập.')
    else:
        form = ProductForm(instance=product)

    images_by_type: Dict[str, Any] = {}
    if product:
        images_by_type['gallery'] = product.images.all()

    context = {
        'product': product,
        'form': form,
        'categories': Category.objects.all(),
        'mode': mode,
        'images_by_type': images_by_type,
    }
    return render(request, 'product_detail.html', context)


@login_required
@admin_required
@require_POST
def toggle_product_visibility(request: HttpRequest, pk: int) -> JsonResponse:
    try:
        product = selectors.get_product_by_id(pk)
        data = json.loads(request.body)
        is_visible = data.get('is_visible', True)
        new_status = ProductsService.toggle_visibility(product, is_visible)
        return JsonResponse({'status': 'success', 'is_active': new_status})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
@admin_required
@require_POST
def delete_product_image(request: HttpRequest, img_id: int) -> JsonResponse:
    try:
        image = ProductImage.objects.get(id=img_id)
        image.delete()
        return JsonResponse({'status': 'success', 'message': 'Đã xóa ảnh thành công'})
    except ProductImage.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Không tìm thấy ảnh'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
