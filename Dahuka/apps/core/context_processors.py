# --- CONTEXT PROCESSORS ---
# Những hàm này giúp đưa dữ liệu vào TẤT CẢ các template tự động (ví dụ: số thông báo trên Navbar)

def notification_counts(request):
    """Đếm số thông báo chưa đọc và phân loại theo vai trò để hiển thị trên Navbar."""
    if not request.user.is_authenticated:
        return {}

    from apps.core.models import Notification

    # Đếm tổng số thông báo chưa đọc của người dùng hiện tại
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()

    return {
        "unread_notification_count": count,
        "admin_notification_count": count if request.user.is_superuser else 0,
        "staff_notification_count": (
            count if request.user.is_staff and not request.user.is_superuser else 0
        ),
        "customer_notification_count": (
            count if not request.user.is_superuser and not request.user.is_staff else 0
        ),
    }


def global_categories(request):
    """Lấy danh sách danh mục sản phẩm để hiển thị ở Menu/Dropdown trên toàn trang web."""
    from apps.categories.models import Category

    # Lấy tất cả danh mục, sắp xếp theo ID
    all_cats = Category.objects.all().order_by("id")

    # Phân loại: Lọc ra các danh mục máy lọc nước (loại bỏ linh kiện và dịch vụ)
    excluded_slugs = ["linh-kien", "dich-vu"]
    water_categories = [c for c in all_cats if c.slug not in excluded_slugs]

    return {"all_categories": all_cats, "water_categories": water_categories}
