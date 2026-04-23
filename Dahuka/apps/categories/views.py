from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from apps.core.decorators import staff_required
from apps.core.utils import get_paginated_data
from django.http import JsonResponse
from django.contrib import messages
from .models import Category
from .services import CategoryService
from .forms import CategoryForm
from apps.products.services import ProductsService


@login_required
@staff_required
def category_list(request):
    query = request.GET.get("q", "")
    categories_qs = Category.objects.all().order_by("id")

    if query:
        from django.db.models import Q

        categories_qs = categories_qs.filter(
            Q(code__icontains=query) | Q(name__icontains=query)
        )

    page_obj = get_paginated_data(categories_qs, request, 10)

    context = {
        "page_obj": page_obj,
        "query": query,
    }
    return render(request, "categories_list.html", context)


@login_required
@staff_required
def category_add(request):
    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Đã thêm danh mục "{category.name}" thành công.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    return redirect("categories:category_list")


@login_required
@staff_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(
                request, f'Đã cập nhật danh mục "{category.name}" thành công.'
            )
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    return redirect("categories:category_list")


@login_required
@staff_required
def category_delete(request, pk):
    if request.method == "POST":
        category = get_object_or_404(Category, pk=pk)
        name = category.name
        category.delete()
        messages.success(request, f'Đã xóa danh mục "{name}" thành công.')
    return redirect("categories:category_list")


@login_required
@staff_required
def get_category_products(request, pk):
    category = get_object_or_404(Category, pk=pk)
    products = ProductsService.format_products_for_dropdown(category)
    return JsonResponse({"products": products})
