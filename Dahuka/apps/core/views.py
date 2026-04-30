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
        return redirect("core:admin_dashboard")  # Changed to dashboard
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
    
    products_list = Product.objects.filter(is_active=True)
    
    # Search logic
    query = request.GET.get("q")
    if query:
        from django.db.models import Q
        products_list = products_list.filter(
            Q(name__icontains=query) | 
            Q(sku__icontains=query) | 
            Q(category__name__icontains=query)
        ).distinct()

    is_water_purifier = True
    
    current_category = None
    if category_id:
        try:
            current_category = Category.objects.get(id=category_id)
            if current_category.slug in ['linh-kien', 'dich-vu']:
                is_water_purifier = False
        except Category.DoesNotExist:
            pass
        products_list = products_list.filter(category_id=category_id)
    elif category_slug:
        current_category = Category.objects.filter(slug=category_slug).first()
        if category_slug in ['linh-kien', 'dich-vu']:
            is_water_purifier = False
        products_list = products_list.filter(category__slug=category_slug)
    else:
        # Mặc định (Máy lọc nước): ẩn Linh kiện và Dịch vụ
        products_list = products_list.exclude(category__slug__in=['linh-kien', 'dich-vu'])
        
    # Filter by cores
    if filter_cores and is_water_purifier:
        # spec_filters_count format "10 lõi" or "10"
        from django.db.models import Q
        core_q = Q()
        for core in filter_cores:
            core_q |= Q(spec_filters_count__icontains=core)
        products_list = products_list.filter(core_q)
        
    # Filter by prices
    if filter_prices:
        from django.db.models import Q
        price_q = Q()
        for p in filter_prices:
            if p == '4-6':
                price_q |= Q(price__gte=4000000, price__lte=6000000)
            elif p == '6-8':
                price_q |= Q(price__gte=6000000, price__lte=8000000)
            elif p == '8-10':
                price_q |= Q(price__gte=8000000, price__lte=10000000)
            elif p == '10+':
                price_q |= Q(price__gt=10000000)
        products_list = products_list.filter(price_q)

    # Sort
    if sort_by == 'oldest':
        products_list = products_list.order_by("spec_release_year", "id")
    else:
        products_list = products_list.order_by("-spec_release_year", "-id")

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
        },
    )


def view_product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if not product.is_active and not request.user.is_staff:
        from django.http import Http404
        raise Http404
        
    images_by_type = {
        'gallery': product.images.filter(image_type='gallery'),
        'specs': product.images.filter(image_type='specs'),
        'features': product.images.filter(image_type='features'),
        'description': product.images.filter(image_type='description'),
    }
    
    return render(request, "view_product_detail.html", {
        "product": product,
        "images_by_type": images_by_type
    })

@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    from django.contrib.auth.models import User
    from apps.account.models import Customer
    from django.utils import timezone
    from datetime import datetime, timedelta
    import calendar

    # Mặc định là Lọc theo Ngày (Hôm nay)
    filter_type = request.GET.get('filter', 'day')
    date_str = request.GET.get('date')
    
    if date_str:
        try:
            now = datetime.strptime(date_str, "%Y-%m-%d")
            now = timezone.make_aware(now)
        except:
            now = timezone.localtime()
    else:
        now = timezone.localtime()

    start_date = None
    prev_date = None
    next_date = None
    display_label = ""
    
    # Logic xác định khoảng thời gian lọc và các mốc điều hướng
    if filter_type == 'day':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        prev_date = (start_date - timedelta(days=1)).strftime("%Y-%m-%d")
        next_date = (start_date + timedelta(days=1)).strftime("%Y-%m-%d")
        display_label = start_date.strftime("%d/%m/%Y")
        
    elif filter_type == 'month':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if start_date.month == 12:
            end_date = start_date.replace(year=start_date.year + 1, month=1)
        else:
            end_date = start_date.replace(month=start_date.month + 1)
        
        last_day_prev_month = start_date - timedelta(days=1)
        prev_date = last_day_prev_month.replace(day=1).strftime("%Y-%m-%d")
        next_date = end_date.strftime("%Y-%m-%d")
        display_label = f"Tháng {start_date.month}/{start_date.year}"
        
    elif filter_type == 'quarter':
        quarter = (now.month - 1) // 3 + 1
        start_month = (quarter - 1) * 3 + 1
        start_date = now.replace(month=start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Kết thúc quý là cuối tháng thứ 3 kể từ start_month
        end_month = start_month + 2
        last_day = calendar.monthrange(now.year, end_month)[1]
        end_date = now.replace(month=end_month, day=last_day, hour=23, minute=59, second=59) + timedelta(seconds=1)
        
        # Điều hướng quý
        prev_q_date = (start_date - timedelta(days=1)).replace(day=1)
        prev_date = prev_q_date.strftime("%Y-%m-%d")
        next_date = end_date.strftime("%Y-%m-%d")
        display_label = f"Quý {quarter}/{now.year}"

    elif filter_type == 'year':
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date.replace(year=start_date.year + 1)
        prev_date = start_date.replace(year=start_date.year - 1).strftime("%Y-%m-%d")
        next_date = end_date.strftime("%Y-%m-%d")
        display_label = f"Năm {start_date.year}"
    
    else: # Default/All
        start_date = now - timedelta(days=30)
        end_date = now + timedelta(days=1)
        display_label = "30 ngày gần nhất"

    # Base Queryset
    orders_qs = Order.objects.all()
    
    # 1. Thống kê tổng quan (Thẻ Card)
    current_orders = orders_qs.filter(created_at__gte=start_date, created_at__lt=end_date)
    completed_orders = orders_qs.filter(status="completed", updated_at__gte=start_date, updated_at__lt=end_date)
    total_rev = completed_orders.aggregate(rev=Sum("total_amount"))["rev"] or 0
    total_orders = current_orders.count()
    pending_orders = current_orders.filter(status="pending").count()
    total_customers = Customer.objects.count()

    # Average Order Value (AOV)
    aov = total_rev / completed_orders.count() if completed_orders.count() > 0 else 0

    # Operational Efficiency
    finished_orders_count = completed_orders.count() + orders_qs.filter(status="cancelled", created_at__gte=start_date, created_at__lt=end_date).count()
    success_rate = (completed_orders.count() / finished_orders_count * 100) if finished_orders_count > 0 else 0
    cancel_rate = (orders_qs.filter(status="cancelled", created_at__gte=start_date, created_at__lt=end_date).count() / finished_orders_count * 100) if finished_orders_count > 0 else 0

    # New vs Returning Customers
    current_customer_ids = current_orders.values_list('customer_id', flat=True).distinct()
    new_customers_count = 0
    returning_customers_count = 0
    
    for cid in current_customer_ids:
        has_ordered_before = orders_qs.filter(customer_id=cid, created_at__lt=start_date).exists()
        if has_ordered_before:
            returning_customers_count += 1
        else:
            new_customers_count += 1
    if filter_type == 'month':
        if start_date.month == 1:
            start_date_prev = start_date.replace(year=start_date.year - 1, month=12)
        else:
            start_date_prev = start_date.replace(month=start_date.month - 1)
        end_date_prev = start_date
    elif filter_type == 'year':
        start_date_prev = start_date.replace(year=start_date.year - 1)
        end_date_prev = start_date
    elif filter_type == 'day':
        start_date_prev = start_date - timedelta(days=1)
        end_date_prev = start_date
    else:
        delta = end_date - start_date
        start_date_prev = start_date - delta
        end_date_prev = start_date

    # Label for previous period (for tooltips)
    if filter_type == 'month':
        prev_period_label = f"tháng {start_date_prev.month}/{start_date_prev.year}"
    elif filter_type == 'year':
        prev_period_label = f"năm {start_date_prev.year}"
    elif filter_type == 'day':
        prev_period_label = "hôm qua"
    else:
        prev_period_label = "kỳ trước"

    prev_rev = orders_qs.filter(status="completed", updated_at__gte=start_date_prev, updated_at__lt=end_date_prev).aggregate(rev=Sum("total_amount"))["rev"] or 0
    rev_growth = ((total_rev - prev_rev) / prev_rev * 100) if prev_rev > 0 else (100 if total_rev > 0 else 0)
    rev_growth_abs = abs(rev_growth)

    # 2. Biểu đồ đường
    chart_labels = []
    chart_values = []
    
    if filter_type == 'day':
        for h in [0, 4, 8, 12, 16, 20, 24]:
            chart_labels.append(f"{h}h")
            if h == 24:
                # Point at 24h is same as 0h of next day, but for chart we can just show 0
                chart_values.append(0)
            else:
                rev = completed_orders.filter(updated_at__hour__gte=h, updated_at__hour__lt=h+4).aggregate(r=Sum("total_amount"))["r"] or 0
                chart_values.append(int(rev))
            
    elif filter_type == 'month':
        num_days = calendar.monthrange(start_date.year, start_date.month)[1]
        for i in range(1, num_days + 1):
            chart_labels.append(str(i))
            d = start_date.replace(day=i)
            rev = completed_orders.filter(updated_at__date=d.date()).aggregate(r=Sum("total_amount"))["r"] or 0
            chart_values.append(int(rev))
            
    elif filter_type == 'quarter':
        # Hiển thị 3 tháng của quý
        for m in range(start_month, start_month + 3):
            chart_labels.append(f"T{m}")
            m_start = start_date.replace(month=m)
            if m == 12:
                m_end = m_start.replace(year=m_start.year + 1, month=1)
            else:
                m_end = m_start.replace(month=m + 1)
            rev = completed_orders.filter(updated_at__gte=m_start, updated_at__lt=m_end).aggregate(r=Sum("total_amount"))["r"] or 0
            chart_values.append(int(rev))

    elif filter_type == 'year':
        for m in range(1, 13):
            chart_labels.append(f"T{m}")
            m_start = start_date.replace(month=m)
            if m == 12:
                m_end = m_start.replace(year=m_start.year + 1, month=1)
            else:
                m_end = m_start.replace(month=m + 1)
            rev = completed_orders.filter(updated_at__gte=m_start, updated_at__lt=m_end).aggregate(r=Sum("total_amount"))["r"] or 0
            chart_values.append(int(rev))
    
    else:
        for i in range(0, 31, 5):
            d = (start_date + timedelta(days=i)).date()
            chart_labels.append(d.strftime("%d/%m"))
            rev = completed_orders.filter(created_at__date=d).aggregate(r=Sum("total_amount"))["r"] or 0
            chart_values.append(int(rev))

    # 3. Biểu đồ tròn
    items_qs = OrderItem.objects.filter(order__updated_at__gte=start_date, order__updated_at__lt=end_date)
    cat_revenue = items_qs.filter(order__status="completed").values("product__category__name").annotate(total=Sum(F("price") * F("quantity"))).order_by("-total")
    cat_labels = [c["product__category__name"] or "Khác" for c in cat_revenue]
    cat_values = [int(c["total"]) for c in cat_revenue]

    # 4. Top 5 & Khác
    top_products_data = items_qs.filter(order__status="completed").values("product__name").annotate(total_qty=Sum("quantity")).order_by("-total_qty")[:5]
    top_products = list(top_products_data)
    
    # Fallback to All-Time if current period is empty
    is_fallback = False
    if not top_products:
        is_fallback = True
        top_products_data = OrderItem.objects.filter(order__status="completed").values("product__name").annotate(total_qty=Sum("quantity")).order_by("-total_qty")[:5]
        top_products = list(top_products_data)

    if top_products:
        total_top_qty = sum(item["total_qty"] for item in top_products)
        for item in top_products:
            item["percentage"] = int((item["total_qty"] / total_top_qty * 100)) if total_top_qty > 0 else 0

    low_stock = Product.objects.filter(stock__lt=10).order_by("stock")
    recent_orders = orders_qs.order_by("-created_at")[:5]

    context = {
        "prev_period_label": prev_period_label,
        "top_products_is_fallback": is_fallback,
        "total_rev": total_rev,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "total_customers": total_customers,
        "aov": aov,
        "success_rate": success_rate,
        "cancel_rate": cancel_rate,
        "new_customers": new_customers_count,
        "returning_customers": returning_customers_count,
        "rev_growth": rev_growth,
        "rev_growth_abs": rev_growth_abs,
        "chart_labels": chart_labels,
        "chart_values": chart_values,
        "cat_labels": cat_labels,
        "cat_values": cat_values,
        "top_products": top_products,
        "low_stock": low_stock,
        "recent_orders": recent_orders,
        "current_filter": filter_type,
        "prev_date": prev_date,
        "next_date": next_date,
        "display_label": display_label,
        "current_date_iso": start_date.strftime("%Y-%m-%d"),
        "current_month_iso": start_date.strftime("%Y-%m"),
        "current_year": start_date.year,
        "current_quarter": (start_date.month - 1) // 3 + 1,
    }

    return render(request, "core/dashboard.html", context)







def product_comparison(request):
    # Ưu tiên lấy ID từ POST (khi nhấn từ catalog), nếu không có thì lấy từ GET (khi reload trang)
    product_ids = request.POST.getlist('id') if request.method == 'POST' else request.GET.getlist('id')
    
    # Lấy các đối tượng sản phẩm đang kinh doanh từ database
    unordered_products = Product.objects.filter(id__in=product_ids, is_active=True)
    
    # Sắp xếp lại danh sách sản phẩm theo đúng thứ tự ID được gửi lên
    # (Để sản phẩm nào chọn trước sẽ đứng trước)
    product_map = {str(p.id): p for p in unordered_products}
    products = [product_map[str(pid)] for pid in product_ids if str(pid) in product_map]
    
    # Lấy tất cả sản phẩm đang kinh doanh để hiển thị trong Modal chọn thêm (loại bỏ những sản phẩm đã chọn)
    all_products = Product.objects.filter(is_active=True).exclude(id__in=product_ids).order_by('-id')
    
    # Chuyển đổi danh sách ID hiện tại sang dạng JSON để JavaScript xử lý dễ dàng
    current_product_ids = [str(p.id) for p in products]
    
    context = {
        "products": products,
        "all_products": all_products,
        "current_product_ids": current_product_ids,
    }
    return render(request, "product_comparison.html", context)
