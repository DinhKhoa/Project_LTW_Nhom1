from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from apps.products.models import Product
from apps.categories.models import Category
from apps.orders.models import Order
from .models import HomePageSettings
from .selectors import get_admin_dashboard_data, get_catalog_products
from .services import CoreService

@user_passes_test(lambda u: u.is_superuser)
def update_home_settings(request):
    if request.method == "POST":
        CoreService.update_home_page_settings(
            banner_image=request.FILES.get("banner_image"),
            dahuka_pro_image=request.FILES.get("dahuka_pro_image"),
            dahuka_pro_title=request.POST.get("dahuka_pro_title"),
            dahuka_pro_desc=request.POST.get("dahuka_pro_desc")
        )
    return redirect("core:home")

def login_success(request):
    if request.user.is_superuser:
        return redirect("core:admin_dashboard")
    elif request.user.is_staff:
        return redirect("tasks:task_list")
    else:
        return redirect("core:home")

def index(request):
    home_settings = HomePageSettings.objects.first()
    if not home_settings:
        home_settings = HomePageSettings.objects.create()

    featured_products = home_settings.featured_products.all()
    if not featured_products:
        featured_products = Product.objects.filter(is_active=True)[:4]

    return render(
        request,
        "home.html",
        {"home_settings": home_settings, "featured_products": featured_products},
    )

def product_catalog(request):
    category_id = request.GET.get("category")
    category_slug = request.GET.get("cat")
    sort_by = request.GET.get("sort", "newest")
    filter_cores = request.GET.getlist("core")
    filter_prices = request.GET.getlist("price")
    query = request.GET.get("q")
    
    
    products_list, current_category, is_water_purifier = get_catalog_products(
        category_id=category_id,
        category_slug=category_slug,
        sort_by=sort_by,
        filter_cores=filter_cores,
        filter_prices=filter_prices,
        query=query
    )

    paginator = Paginator(products_list, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    categories = Category.objects.all()
    
    template_name = "view_products.html"
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        template_name = "partials/product_list_partial.html"

    return render(
        request,
        template_name,
        {
            "products": page_obj,
            "categories": categories,
            "selected_category": category_id,
            "is_water_purifier": is_water_purifier,
            "current_sort": sort_by,
            "selected_cores": filter_cores,
            "selected_prices": filter_prices,
            "current_category": current_category,
            "cat_slug": category_slug,
            "query": query,
        },
    )

def view_product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if not product.is_active and not request.user.is_staff:
        from django.http import Http404
        raise Http404
        
    images_by_type = {
        'gallery': product.images.all(),
    }
    
    return render(request, "view_product_detail.html", {
        "product": product,
        "images_by_type": images_by_type
    })

@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    filter_type = request.GET.get('filter', 'day')
    date_str = request.GET.get('date')
    
    
    stats = get_admin_dashboard_data(filter_type=filter_type, date_str=date_str)
    
    
    stats["low_stock"] = Product.objects.filter(stock__lt=10).order_by("stock")
    stats["recent_orders"] = Order.objects.order_by("-created_at")[:5]
    
    return render(request, "core/dashboard.html", stats)

def product_comparison(request):
    product_ids = request.POST.getlist('id') if request.method == 'POST' else request.GET.getlist('id')
    unordered_products = Product.objects.filter(id__in=product_ids, is_active=True)
    product_map = {str(p.id): p for p in unordered_products}
    products = [product_map[str(pid)] for pid in product_ids if str(pid) in product_map]
    all_products = Product.objects.filter(is_active=True).exclude(id__in=product_ids).order_by('-id')
    current_product_ids = [str(p.id) for p in products]
    
    return render(request, "product_comparison.html", {
        "products": products,
        "all_products": all_products,
        "current_product_ids": current_product_ids,
    })
