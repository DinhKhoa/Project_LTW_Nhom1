from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .models import Category
from .services import CategoryService


def is_staff(user):
    return user.is_staff

@user_passes_test(is_staff)
def category_list(request):
    query = request.GET.get('q', '')
    page_number = request.GET.get('page', 1)
    
    page_obj = CategoryService.get_categories(query, page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'categories/categories_list.html', context)


@user_passes_test(is_staff)
def category_add(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        success, _, errors = CategoryService.validate_and_create(name)

        if success:
            messages.success(request, f'Đã thêm danh mục "{name}" thành công.')
        else:
            for error in errors.values():
                messages.error(request, error)

    return redirect('categories:category_list')


@user_passes_test(is_staff)
def category_edit(request, pk):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        success, _, errors = CategoryService.validate_and_update(pk, name)

        if success:
            messages.success(request, 'Cập nhật danh mục thành công.')
        else:
            for error in errors.values():
                messages.error(request, error)

    return redirect('categories:category_list')


@user_passes_test(is_staff)
def category_delete(request, pk):
    if request.method == 'POST':
        category = get_object_or_404(Category, pk=pk)
        ten = category.name
        category.delete()
        messages.success(request, f'Đã xóa danh mục "{ten}" thành công.')
    
    return redirect('categories:category_list')


def products_by_category(request, pk):
    """API endpoint returns list of products by category (for dropdown)"""
    category = get_object_or_404(Category, pk=pk)
    query_ma = request.GET.get('ma', '')

    products = CategoryService.format_products_for_dropdown(category, query_ma)

    return JsonResponse({'products': products, 'category': category.name})
