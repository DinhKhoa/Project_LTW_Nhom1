from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.contrib import messages
from typing import Any

from apps.core.decorators import admin_required
from apps.core.utils import get_paginated_data
from apps.products.services import ProductsService

from .selectors import search_categories, get_category_by_id
from .services import CategoryService

@login_required
@admin_required
def category_list(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("q", "")
    categories_qs = search_categories(query)
    page_obj = get_paginated_data(categories_qs, request, 10)

    return render(request, "categories_list.html", {
        "page_obj": page_obj,
        "query": query,
    })

@login_required
@admin_required
def category_add(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        success, category, errors = CategoryService.create_category(request.POST, request.FILES)
        if success:
            messages.success(request, f'Đã thêm danh mục "{category.name}" thành công.')
        else:
            for field, field_errors in errors.items():
                for error in field_errors:
                    messages.error(request, f"{field}: {error}")
    
    return redirect("categories:category_list")

@login_required
@admin_required
def category_edit(request: HttpRequest, pk: int) -> HttpResponse:
    category = get_category_by_id(pk)
    if request.method == "POST":
        success, category, errors = CategoryService.update_category(category, request.POST, request.FILES)
        if success:
            messages.success(request, f'Đã cập nhật danh mục "{category.name}" thành công.')
        else:
            for field, field_errors in errors.items():
                for error in field_errors:
                    messages.error(request, f"{field}: {error}")
                    
    return redirect("categories:category_list")

@login_required
@admin_required
def category_delete(request: HttpRequest, pk: int) -> HttpResponse:
    if request.method == "POST":
        category = get_category_by_id(pk)
        success, name = CategoryService.delete_category(category)
        if success:
            messages.success(request, f'Đã xóa danh mục "{name}" thành công.')
            
    return redirect("categories:category_list")

@login_required
@admin_required
def get_category_products(request: HttpRequest, pk: int) -> JsonResponse:
    category = get_category_by_id(pk)
    products = ProductsService.format_products_for_dropdown(category)
    return JsonResponse({"products": products})
