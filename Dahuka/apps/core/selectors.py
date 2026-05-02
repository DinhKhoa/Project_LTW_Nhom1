# Chứa các hàm truy vấn dữ liệu (Read-only) cho app Core
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from datetime import datetime, timedelta
import calendar
from apps.orders.models import Order, OrderItem
from apps.account.models import Customer
from apps.products.models import Product
from apps.categories.models import Category

def get_admin_dashboard_data(filter_type='day', date_str=None):
    """
    Tính toán và trả về toàn bộ thông số cho Admin Dashboard.
    """
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
    
    # Logic xác định khoảng thời gian lọc
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
        end_month = start_month + 2
        last_day = calendar.monthrange(now.year, end_month)[1]
        end_date = now.replace(month=end_month, day=last_day, hour=23, minute=59, second=59) + timedelta(seconds=1)
        prev_date = (start_date - timedelta(days=1)).replace(day=1).strftime("%Y-%m-%d")
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

    orders_qs = Order.objects.all()
    
    # 1. Thống kê tổng quan
    current_orders = orders_qs.filter(created_at__gte=start_date, created_at__lt=end_date)
    completed_orders = orders_qs.filter(status="completed", updated_at__gte=start_date, updated_at__lt=end_date)
    total_rev = completed_orders.aggregate(rev=Sum("total_amount"))["rev"] or 0
    total_orders = current_orders.count()
    pending_orders = current_orders.filter(status="pending").count()
    total_customers = Customer.objects.count()

    aov = total_rev / completed_orders.count() if completed_orders.count() > 0 else 0
    finished_count = completed_orders.count() + orders_qs.filter(status="cancelled", created_at__gte=start_date, created_at__lt=end_date).count()
    success_rate = (completed_orders.count() / finished_count * 100) if finished_count > 0 else 0
    cancel_rate = (orders_qs.filter(status="cancelled", created_at__gte=start_date, created_at__lt=end_date).count() / finished_count * 100) if finished_count > 0 else 0

    # New vs Returning
    guest_count = current_orders.filter(customer__isnull=True).count()
    reg_ids = current_orders.exclude(customer__isnull=True).values_list('customer_id', flat=True).distinct()
    new_count = 0
    ret_count = 0
    for cid in reg_ids:
        if orders_qs.filter(customer_id=cid, created_at__lt=start_date).exists(): ret_count += 1
        else: new_count += 1

    # Growth
    if filter_type == 'month':
        start_date_prev = (start_date - timedelta(days=1)).replace(day=1)
        prev_period_label = f"tháng {start_date_prev.month}/{start_date_prev.year}"
    elif filter_type == 'year':
        start_date_prev = start_date.replace(year=start_date.year - 1)
        prev_period_label = f"năm {start_date_prev.year}"
    elif filter_type == 'day':
        start_date_prev = start_date - timedelta(days=1)
        prev_period_label = "hôm qua"
    else:
        start_date_prev = start_date - (end_date - start_date)
        prev_period_label = "kỳ trước"
    
    end_date_prev = start_date
    prev_rev = orders_qs.filter(status="completed", updated_at__gte=start_date_prev, updated_at__lt=end_date_prev).aggregate(rev=Sum("total_amount"))["rev"] or 0
    rev_growth = ((total_rev - prev_rev) / prev_rev * 100) if prev_rev > 0 else (100 if total_rev > 0 else 0)

    # 2. Chart Logic
    chart_labels, chart_values = [], []
    if filter_type == 'day':
        for h in [0, 4, 8, 12, 16, 20]:
            chart_labels.append(f"{h}h")
            rev = completed_orders.filter(updated_at__hour__gte=h, updated_at__hour__lt=h+4).aggregate(r=Sum("total_amount"))["r"] or 0
            chart_values.append(int(rev))
    elif filter_type == 'month':
        num_days = calendar.monthrange(start_date.year, start_date.month)[1]
        for i in range(1, num_days + 1):
            chart_labels.append(str(i))
            rev = completed_orders.filter(updated_at__date=start_date.replace(day=i).date()).aggregate(r=Sum("total_amount"))["r"] or 0
            chart_values.append(int(rev))
    elif filter_type == 'quarter':
        for i in range(3):
            month = start_date.month + i
            chart_labels.append(f"Tháng {month}")
            rev = completed_orders.filter(updated_at__month=month, updated_at__year=start_date.year).aggregate(r=Sum("total_amount"))["r"] or 0
            chart_values.append(int(rev))
    elif filter_type == 'year':
        for month in range(1, 13):
            chart_labels.append(f"T.{month}")
            rev = completed_orders.filter(updated_at__month=month, updated_at__year=start_date.year).aggregate(r=Sum("total_amount"))["r"] or 0
            chart_values.append(int(rev))
    else: # 30 ngày gần nhất
        for i in range(29, -1, -1):
            day = (timezone.localtime() - timedelta(days=i)).date()
            chart_labels.append(day.strftime("%d/%m"))
            rev = completed_orders.filter(updated_at__date=day).aggregate(r=Sum("total_amount"))["r"] or 0
            chart_values.append(int(rev))

    # 3. Categories & Products
    items_qs = OrderItem.objects.filter(order__updated_at__gte=start_date, order__updated_at__lt=end_date)
    cat_revenue = items_qs.filter(order__status="completed").values("product__category__name").annotate(total=Sum(F("price") * F("quantity"))).order_by("-total")
    cat_labels = [c["product__category__name"] or "Khác" for c in cat_revenue]
    cat_values = [int(c["total"]) for c in cat_revenue]

    top_products_data = items_qs.filter(order__status="completed").values("product__name").annotate(total_qty=Sum("quantity")).order_by("-total_qty")[:5]
    top_products = list(top_products_data)
    is_fallback = False
    if not top_products:
        is_fallback = True
        top_products = list(OrderItem.objects.filter(order__status="completed").values("product__name").annotate(total_qty=Sum("quantity")).order_by("-total_qty")[:5])

    if top_products:
        total_top_qty = sum(item["total_qty"] for item in top_products)
        for item in top_products:
            item["percentage"] = int((item["total_qty"] / total_top_qty * 100)) if total_top_qty > 0 else 0

    return {
        "total_rev": total_rev, "total_orders": total_orders, "pending_orders": pending_orders,
        "total_customers": total_customers, "aov": aov, "success_rate": success_rate,
        "cancel_rate": cancel_rate, "new_customers": new_count, "returning_customers": ret_count,
        "guest_customers": guest_count, "rev_growth": rev_growth, "rev_growth_abs": abs(rev_growth),
        "chart_labels": chart_labels, "chart_values": chart_values, "cat_labels": cat_labels,
        "cat_values": cat_values, "top_products": top_products, "top_products_is_fallback": is_fallback,
        "display_label": display_label, "prev_date": prev_date, "next_date": next_date,
        "prev_period_label": prev_period_label, "current_filter": filter_type,
        "current_date_iso": start_date.strftime("%Y-%m-%d"),
        "current_month_iso": start_date.strftime("%Y-%m"),
        "current_year": start_date.year,
        "current_quarter": (start_date.month - 1) // 3 + 1,
    }

def get_catalog_products(category_id=None, category_slug=None, sort_by='newest', filter_cores=None, filter_prices=None, query=None):
    """
    Truy vấn và lọc danh sách sản phẩm.
    """
    products_list = Product.objects.filter(is_active=True)
    if query:
        products_list = products_list.filter(name__icontains=query).distinct()

    is_water_purifier = True
    current_category = None

    if category_id:
        current_category = Category.objects.filter(id=category_id).first()
        if current_category and current_category.slug in ['linh-kien', 'dich-vu']: is_water_purifier = False
        products_list = products_list.filter(category_id=category_id)
    elif category_slug:
        current_category = Category.objects.filter(slug=category_slug).first()
        if category_slug in ['linh-kien', 'dich-vu']: is_water_purifier = False
        products_list = products_list.filter(category__slug=category_slug)
    else:
        products_list = products_list.exclude(category__slug__in=['linh-kien', 'dich-vu'])

    if filter_cores and is_water_purifier:
        core_q = Q()
        for core in filter_cores: core_q |= Q(spec_filters_count__icontains=core)
        products_list = products_list.filter(core_q)

    if filter_prices:
        price_q = Q()
        for p in filter_prices:
            if p == '4-6': price_q |= Q(price__gte=4000000, price__lte=6000000)
            elif p == '6-8': price_q |= Q(price__gte=6000000, price__lte=8000000)
            elif p == '8-10': price_q |= Q(price__gte=8000000, price__lte=10000000)
            elif p == '10+': price_q |= Q(price__gt=10000000)
        products_list = products_list.filter(price_q)

    if sort_by == 'oldest': products_list = products_list.order_by("spec_release_year", "id")
    else: products_list = products_list.order_by("-spec_release_year", "-id")

    return products_list, current_category, is_water_purifier
