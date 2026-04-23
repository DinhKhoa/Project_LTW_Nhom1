from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .models import HomePageSettings
from apps.products.models import Product
from apps.categories.models import Category
from apps.orders.models import Order, OrderItem
from django.core.paginator import Paginator
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import timedelta


@user_passes_test(lambda u: u.is_superuser)
def update_home_settings(request):
    if request.method == "POST":
        settings = HomePageSettings.objects.first()
        if not settings:
            settings = HomePageSettings.objects.create()

        if "banner_image" in request.FILES:
            settings.banner_image = request.FILES["banner_image"]
        if "mutosi_pro_image" in request.FILES:
            settings.mutosi_pro_image = request.FILES["mutosi_pro_image"]
        if "mutosi_pro_title" in request.POST:
            settings.mutosi_pro_title = request.POST["mutosi_pro_title"]
        if "mutosi_pro_desc" in request.POST:
            settings.mutosi_pro_desc = request.POST["mutosi_pro_desc"]

        settings.save()
    return redirect("core:home")


def login_success(request):
    if request.user.is_superuser:
        return redirect("core:admin_dashboard") # Changed to dashboard
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
    products_list = Product.objects.filter(is_active=True)
    if category_id:
        products_list = products_list.filter(category_id=category_id)
    products_list = products_list.order_by("-id")

    paginator = Paginator(products_list, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    categories = Category.objects.all()
    return render(request, "view_products.html", {"products": page_obj, "categories": categories, "selected_category": category_id})


def view_product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if not product.is_active and not request.user.is_staff:
        from django.http import Http404
        raise Http404
    return render(request, "view_product_detail.html", {"product": product})


@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    # Tổng hợp số liệu
    total_rev = Order.objects.filter(status='completed').aggregate(rev=Sum('total_amount'))['rev'] or 0
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    
    # Biểu đồ doanh thu 7 ngày gần nhất
    days = []
    rev_data = []
    for i in range(6, -1, -1):
        d = timezone.now().date() - timedelta(days=i)
        days.append(d.strftime('%d/%m'))
        daily_rev = Order.objects.filter(created_at__date=d, status='completed').aggregate(rev=Sum('total_amount'))['rev'] or 0
        rev_data.append(int(daily_rev))
        
    # Top 5 sản phẩm bán chạy
    top_products = OrderItem.objects.values('product__name').annotate(total_qty=Sum('quantity')).order_by('-total_qty')[:5]
    
    # Cảnh báo tồn kho thấp (<10)
    low_stock = Product.objects.filter(stock__lt=10).order_by('stock')
    
    # Đơn hàng gần đây
    recent_orders = Order.objects.all().order_by('-created_at')[:5]

    context = {
        'total_rev': total_rev,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'days': days,
        'rev_data': rev_data,
        'top_products': top_products,
        'low_stock': low_stock,
        'recent_orders': recent_orders,
    }
    return render(request, 'core/dashboard.html', context)


def product_comparison(request):
    return render(request, "product_comparison.html")


def product_selection_frame(request):
    return render(request, "product_selection_frame.html")
