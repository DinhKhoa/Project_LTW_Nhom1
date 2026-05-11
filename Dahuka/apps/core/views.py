from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from apps.products.models import Product
from apps.categories.models import Category
from apps.orders.models import Order
from .models import HomePageSettings
from .selectors import get_admin_dashboard_data, get_catalog_products
from .services import CoreService


# ==============================================================================
# GIẢI THÍCH VỀ DECORATOR (Các dòng có dấu @ ở phía trên hàm)
# - Decorator là một "anh bảo vệ" đứng trước cửa các hàm (View).
# - Nhiệm vụ: Kiểm tra điều kiện (ví dụ: đã đăng nhập chưa? có phải admin không?)
#   trước khi cho phép thực thi nội dung bên trong hàm.
# - Giúp code gọn gàng, bảo mật và tái sử dụng được logic kiểm tra quyền ở nhiều nơi.
# ==============================================================================


# Chỉ Superuser mới được dùng chức năng này (decorator kiểm tra quyền)
@user_passes_test(lambda u: u.is_superuser)
def update_home_settings(request):
    """Cập nhật cài đặt trang chủ: banner, ảnh, tiêu đề section Dahuka Pro."""
    if request.method == "POST":
        CoreService.update_home_page_settings(
            banner_image=request.FILES.get("banner_image"),
            dahuka_pro_image=request.FILES.get("dahuka_pro_image"),
            dahuka_pro_title=request.POST.get("dahuka_pro_title"),
            dahuka_pro_desc=request.POST.get("dahuka_pro_desc"),
        )
    return redirect("core:home")


# --- LUỒNG ĐIỀU HƯỚNG & PHÂN QUYỀN (CORE LOGIC) ---


# 1. Điều hướng sau khi đăng nhập (Được gọi từ LOGIN_REDIRECT_URL trong settings.py)
def login_success(request):
    """
    Hàm này đóng vai trò là 'Bộ phân loại người dùng'.
    Sau khi Django xác thực mật khẩu đúng, nó sẽ đẩy User vào đây để kiểm tra vai trò.
    """
    # Nếu là ADMIN tối cao (người quản lý toàn hệ thống)
    if request.user.is_superuser:
        return redirect(
            "core:admin_dashboard"
        )  # Chuyển đến trang xem doanh thu/thống kê

    # Nếu là NHÂN VIÊN (người đi giao hàng)
    elif request.user.is_staff:
        return redirect("tasks:task_list")  # Chuyển đến danh sách đơn hàng cần xử lý

    # Nếu là KHÁCH HÀNG (người mua hàng bình thường)
    else:
        return redirect("core:home")  # Về trang chủ để tiếp tục mua sắm


# Trang chủ của website (ai cũng xem được, không cần đăng nhập)
def index(request):
    """Hiển thị trang chủ với banner và sản phẩm nổi bật."""
    # Lấy cài đặt trang chủ từ DB, nếu chưa có thì tạo mới với giá trị mặc định
    home_settings = HomePageSettings.objects.first()
    if not home_settings:
        home_settings = HomePageSettings.objects.create()

    # Lấy sản phẩm nổi bật do admin chọn; nếu chưa chọn → lấy 4 sản phẩm đầu
    featured_products = home_settings.featured_products.all()
    if not featured_products:
        featured_products = Product.objects.filter(is_active=True)[:4]

    return render(
        request,
        "home.html",
        {"home_settings": home_settings, "featured_products": featured_products},
    )


# Trang catalog sản phẩm công khai (có lọc, tìm kiếm, phân trang)
def product_catalog(request):
    """Danh sách sản phẩm với các bộ lọc: danh mục, giá, số lõi, tìm kiếm."""
    category_id = request.GET.get("category")
    category_slug = request.GET.get("cat")
    sort_by = request.GET.get("sort", "newest")
    filter_cores = request.GET.getlist("core")
    filter_prices = request.GET.getlist("price")
    query = request.GET.get("q")

    # Gọi selector để lấy danh sách sản phẩm đã lọc từ DB
    products_list, current_category, is_water_purifier = get_catalog_products(
        category_id=category_id,
        category_slug=category_slug,
        sort_by=sort_by,
        filter_cores=filter_cores,
        filter_prices=filter_prices,
        query=query,
    )

    # Phân trang: mỗi trang 12 sản phẩm
    paginator = Paginator(products_list, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    categories = Category.objects.all()

    # Nếu là AJAX request → chỉ trả về phần danh sách (không load lại toàn trang)
    template_name = "view_products.html"
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        template_name = "product_list_partial.html"

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


# Trang chi tiết sản phẩm (ai cũng xem được)
def view_product_detail(request, slug):
    """Hiển thị thông tin chi tiết 1 sản phẩm theo slug URL."""
    # Lấy sản phẩm theo slug; nếu không tìm thấy → trả về lỗi 404
    product = get_object_or_404(Product, slug=slug)
    # Sản phẩm bị ẩn (is_active=False) → người thường không xem được
    if not product.is_active and not request.user.is_staff:
        from django.http import Http404

        raise Http404

    # Phân loại hình ảnh: gallery, tính năng, mô tả
    images_by_type = {
        "gallery": product.images.all(),
        "features": product.image_features,
        "description": product.image_description,
    }

    return render(
        request,
        "view_product_detail.html",
        {"product": product, "images_by_type": images_by_type},
    )


# 2. Dashboard quản trị (CHỈ Admin tối cao - Superuser mới được vào)
# @user_passes_test giống như một "Anh bảo vệ" (Bouncer) đứng ở cửa VIP Club.
# Nếu bạn không có thẻ Superuser, anh ấy sẽ mời bạn ra ngoài.
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    """
    Trang tổng quan nhạy cảm: Chứa số liệu tiền nong, doanh thu và tồn kho.

    LƯU Ý VỀ BẢO MẬT:
    - Hiện tại: Nếu không phải Admin, Django sẽ Redirect (chuyển hướng) về trang Login.
    - Tại sao dùng Redirect? Để 'giấu' trang này đi (Security through obscurity), tránh lộ diện trang Admin.
    - Tại sao dùng 403? Nếu muốn báo thẳng là 'Bạn không đủ quyền' (nhanh hơn về hiệu năng nhưng xác nhận trang này có tồn tại).
    """
    filter_type = request.GET.get("filter", "day")
    date_str = request.GET.get("date")

    # Gọi hàm xử lý dữ liệu từ selectors.py để tính toán doanh thu (tách biệt logic)
    stats = get_admin_dashboard_data(filter_type=filter_type, date_str=date_str)

    # Lấy thêm các cảnh báo về kho bãi và các đơn hàng vừa mới phát sinh
    stats["low_stock"] = Product.objects.filter(stock__lt=10).order_by("stock")
    stats["recent_orders"] = Order.objects.order_by("-created_at")[:5]

    return render(request, "core/dashboard.html", stats)


# Trang so sánh sản phẩm
def product_comparison(request):
    """
    Giúp người dùng xem bảng so sánh thông số giữa các sản phẩm (Số lõi, giá, năm ra mắt).
    Hỗ trợ cả phương thức GET (từ link) và POST (từ form chọn sản phẩm).
    """
    # Lấy danh sách ID sản phẩm từ Request
    product_ids = (
        request.POST.getlist("id")
        if request.method == "POST"
        else request.GET.getlist("id")
    )

    # Truy vấn sản phẩm từ DB
    unordered_products = Product.objects.filter(id__in=product_ids, is_active=True)
    product_map = {str(p.id): p for p in unordered_products}

    # Giữ đúng thứ tự sản phẩm như user đã chọn để hiển thị trên bảng
    products = [product_map[str(pid)] for pid in product_ids if str(pid) in product_map]

    # Lấy thêm danh sách sản phẩm khác (để gợi ý thêm vào bảng so sánh)
    all_products = (
        Product.objects.filter(is_active=True)
        .exclude(id__in=product_ids)
        .order_by("-id")
    )
    current_product_ids = [str(p.id) for p in products]

    return render(
        request,
        "product_comparison.html",
        {
            "products": products,
            "all_products": all_products,
            "current_product_ids": current_product_ids,
        },
    )
