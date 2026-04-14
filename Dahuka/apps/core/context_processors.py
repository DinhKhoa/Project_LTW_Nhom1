from apps.orders.models import Order


def notification_counts(request):
    if not request.user.is_authenticated:
        return {}

    counts = {
        "admin_notification_count": 0,
        "staff_notification_count": 0,
        "customer_notification_count": 0,
    }

    if request.user.is_superuser:
        # Admin: Số lượng đơn hàng chưa hoàn thành
        counts["admin_notification_count"] = Order.objects.exclude(
            status__in=["completed", "cancelled"]
        ).count()

    elif request.user.is_staff:
        # Staff: Số lượng đơn hàng được giao cho
        counts["staff_notification_count"] = (
            Order.objects.filter(assigned_staff=request.user)
            .exclude(status__in=["completed", "cancelled"])
            .count()
        )

    else:
        # Customer: Tình trạng thông báo đơn hàng (Đơn hàng đang xử lý của họ)
        try:
            counts["customer_notification_count"] = (
                Order.objects.filter(customer=request.user)
                .exclude(status__in=["completed", "cancelled"])
                .count()
            )
        except Exception:
            pass

    return counts
