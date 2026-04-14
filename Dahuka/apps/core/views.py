from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from .models import HomePageSettings
from apps.products.models import Product
from apps.categories.models import Category
from django.core.paginator import Paginator

@user_passes_test(lambda u: u.is_superuser)
def update_home_settings(request):
    if request.method == 'POST':
        settings = HomePageSettings.objects.first()
        if not settings:
            settings = HomePageSettings.objects.create()
        
        # Update Fields
        if 'banner_image' in request.FILES:
            settings.banner_image = request.FILES['banner_image']
        if 'mutosi_pro_image' in request.FILES:
            settings.mutosi_pro_image = request.FILES['mutosi_pro_image']
        
        if 'mutosi_pro_title' in request.POST:
            settings.mutosi_pro_title = request.POST['mutosi_pro_title']
        if 'mutosi_pro_desc' in request.POST:
            settings.mutosi_pro_desc = request.POST['mutosi_pro_desc']
        
        settings.save()
    return redirect('core:home')

def login_success(request):
    if request.user.is_superuser:
        return redirect('orders:order_list')
    elif request.user.is_staff:
        return redirect('tasks:task_list')
    else:
        return redirect('core:home')

def index(request):
    home_settings = HomePageSettings.objects.first()
    if not home_settings:
        home_settings = HomePageSettings.objects.create()
    
    featured_products = home_settings.featured_products.all()
    if not featured_products:
        featured_products = Product.objects.all()[:4]
        
    return render(request, 'core/home.html', {
        'home_settings': home_settings,
        'featured_products': featured_products
    })

def product_list(request):
    products_list = Product.objects.all().order_by('-id')
    
    # Pagination
    paginator = Paginator(products_list, 12) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    return render(request, 'core/view_products.html', {
        'products': page_obj,
        'categories': categories
    })

def product_detail(request):
    return render(request, 'core/view_product_detail.html')

def product_comparison(request):
    return render(request, 'core/product_comparison.html')

def product_selection_frame(request):
    return render(request, 'core/product_selection_frame.html')
