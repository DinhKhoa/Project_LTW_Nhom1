from apps.orders.models import Order


def notification_counts(request):
    if not request.user.is_authenticated:
        return {}

    from apps.core.models import Notification
    
    # Get unread notification count for the current user
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()

    return {
        "unread_notification_count": count,
        # Keep old variables temporarily to avoid breaking base.html until it's updated
        "admin_notification_count": count if request.user.is_superuser else 0,
        "staff_notification_count": count if request.user.is_staff and not request.user.is_superuser else 0,
        "customer_notification_count": count if not request.user.is_superuser and not request.user.is_staff else 0,
    }


def global_categories(request):
    from apps.categories.models import Category
    all_cats = Category.objects.all().order_by('id')
    
    # Lọc danh mục Máy lọc nước (bỏ Linh kiện và Dịch vụ)
    excluded_slugs = ['linh-kien', 'dich-vu']
    water_categories = [c for c in all_cats if c.slug not in excluded_slugs]
    
    return {
        'all_categories': all_cats,
        'water_categories': water_categories
    }
