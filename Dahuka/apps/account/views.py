# apps/account/views.py
# File này đóng vai trò là Controller (Bộ điều khiển) trong mô hình MVT của Django.
# Nó xử lý mọi yêu cầu liên quan đến tài khoản người dùng, địa chỉ và đơn hàng.

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Prefetch, Q

from apps.core.forms import (
    AddressForm,
    CancelOrderForm,
    CustomerForm,
    PasswordChangeForm,
)
from apps.orders.models import Order, OrderItem
from .services import AccountService
from .forms import RegistrationForm, PublicPasswordChangeForm
from . import selectors
from .decorators import customer_required


# ==============================================================================
# GIẢI THÍCH VỀ DECORATOR (Các dòng có dấu @ ở phía trên hàm)
# - Decorator là một "anh bảo vệ" đứng trước cửa các hàm (View).
# - Nhiệm vụ: Kiểm tra quyền truy cập trước khi chạy code chính của hàm.
# - Ví dụ: @login_required (Yêu cầu đăng nhập), @customer_required (Yêu cầu là khách).
# ==============================================================================


# --- QUẢN LÝ MẬT KHẨU & ĐIỀU HƯỚNG ---

# Đổi mật khẩu công khai (dành cho người chưa đăng nhập - Quên mật khẩu)
def public_change_password(request: HttpRequest) -> HttpResponse:
    """Xác thực bằng SĐT + mật khẩu cũ (giả lập OTP), sau đó cho phép đặt mật khẩu mới."""
    form = PublicPasswordChangeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        phone = form.cleaned_data["phone"]
        current_password = form.cleaned_data["current_password"]
        new_password = form.cleaned_data["new_password"]

        # Kiểm tra xem SĐT và mật khẩu cũ có khớp với User nào không
        user = authenticate(request, username=phone, password=current_password)
        if user is not None:
            user.set_password(new_password) # Mã hóa mật khẩu mới trước khi lưu
            user.save()
            messages.success(
                request, "Đổi mật khẩu thành công. Vui lòng đăng nhập lại."
            )
            return redirect("login")
        else:
            messages.error(
                request, "Số điện thoại hoặc mật khẩu hiện tại không chính xác."
            )

    return render(request, "registration/password_reset_confirm.html", {"form": form})


# Điều phối người dùng đến đúng trang Dashboard dựa theo vai trò
@login_required
def account_dashboard(request: HttpRequest) -> HttpResponse:
    """Điều hướng: Nếu là Admin/Staff thì về trang cá nhân, Khách thì về mục tương ứng."""
    section = request.GET.get("section", "profile")

    # Bảo mật: Ngăn chặn Admin/Staff truy cập vào các mục của Khách hàng thường
    if (request.user.is_staff or request.user.is_superuser) and section in [
        "orders",
        "addresses",
    ]:
        section = "profile"
        messages.warning(
            request, "Tài khoản nhân viên/admin không thể truy cập mục này."
        )

    # Bản đồ điều hướng (Mapping)
    section_map = {
        "orders": "account:purchase_list",
        "addresses": "account:address_list",
        "profile": "account:profile_view",
    }
    return redirect(section_map.get(section, "account:profile_view"))


# --- QUẢN LÝ ĐỊA CHỈ (ADDRESS MANAGEMENT) ---

# Hiển thị danh sách địa chỉ của khách hàng
@login_required
@customer_required
def address_list(request: HttpRequest) -> HttpResponse:
    """Lấy danh sách địa chỉ từ Selector và hiển thị lên giao diện."""
    customer = AccountService.get_or_create_customer(request.user)
    addresses = selectors.get_addresses_for_customer(customer)
    return render(
        request,
        "addresses.html",
        {
            "addresses": addresses,
            "customer": customer,
            "active_section": "addresses",
        },
    )


# Thêm địa chỉ mới (Hỗ trợ AJAX để hiển thị Modal)
@login_required
@customer_required
def add_address(request: HttpRequest) -> HttpResponse:
    """Xử lý thêm địa chỉ: Nếu là AJAX thì trả về JSON/HTML Partial cho Modal."""
    customer = AccountService.get_or_create_customer(request.user)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        if request.method == "POST":
            form = AddressForm(request.POST)
            if form.is_valid():
                # Gọi Service để thực hiện nghiệp vụ lưu địa chỉ
                AccountService.create_address(customer, form.cleaned_data)
                messages.success(request, "Thêm địa chỉ mới thành công")
                return JsonResponse({"success": True})
            else:
                # Nếu Form sai (ví dụ thiếu SĐT), trả về HTML chứa lỗi để hiện lại trong Modal
                html = render_to_string(
                    "partials/_address_form.html",
                    {"form": form, "request": request, "submit_label": "Xác nhận"},
                    request=request,
                )
                return JsonResponse({"success": False, "html": html})
        else:
            # Nếu là GET: Trả về một Form trống để nhúng vào Modal
            form = AddressForm(initial={"address_type": "home"})
            html = render_to_string(
                "partials/_address_form.html",
                {"form": form, "request": request, "submit_label": "Xác nhận"},
                request=request,
            )
            return JsonResponse({"html": html})

    return redirect("account:address_list")


# Chỉnh sửa địa chỉ cũ (Hỗ trợ AJAX)
@login_required
@customer_required
def edit_address(request: HttpRequest, pk: int) -> HttpResponse:
    """Lấy địa chỉ cũ, đưa vào Form và xử lý cập nhật qua AJAX."""
    customer = AccountService.get_or_create_customer(request.user)
    address = selectors.get_address_by_id(customer, pk)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        if request.method == "POST":
            form = AddressForm(request.POST, instance=address)
            if form.is_valid():
                # Gọi Service cập nhật dữ liệu
                AccountService.update_address(customer, address.id, form.cleaned_data)
                messages.success(request, "Cập nhật địa chỉ thành công")
                return JsonResponse({"success": True})
            else:
                html = render_to_string(
                    "partials/_address_form.html",
                    {"form": form, "request": request, "submit_label": "Cập nhật"},
                    request=request,
                )
                return JsonResponse({"success": False, "html": html})
        else:
            # GET: Đưa dữ liệu hiện tại của địa chỉ vào Form để người dùng sửa
            form = AddressForm(instance=address)
            html = render_to_string(
                "partials/_address_form.html",
                {"form": form, "request": request, "submit_label": "Cập nhật"},
                request=request,
            )
            return JsonResponse({"html": html})

    return redirect("account:address_list")


# Xóa địa chỉ (Chỉ chấp nhận phương thức POST để bảo mật)
@login_required
@customer_required
def delete_address(request: HttpRequest, pk: int) -> HttpResponse:
    """Xóa địa chỉ dựa trên ID và chủ sở hữu (Customer)."""
    customer = AccountService.get_or_create_customer(request.user)
    address = selectors.get_address_by_id(customer, pk)

    if request.method == "POST":
        address.delete()
        messages.success(request, "Xóa địa chỉ thành công")
        return redirect("account:address_list")

    return redirect("account:address_list")


# --- THÔNG TIN CÁ NHÂN & BẢO MẬT (PROFILE & SECURITY) ---

# Xem và chỉnh sửa thông tin cá nhân (Profile)
@login_required
def profile_view(request: HttpRequest) -> HttpResponse:
    """Hiển thị và xử lý cập nhật Profile như Tên, Email, SĐT."""
    customer = AccountService.get_or_create_customer(request.user)

    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            # Lưu thông tin (Service sẽ xử lý cập nhật cả bảng User và bảng Customer)
            form.save(user=request.user)
            messages.success(request, "Lưu thông tin thành công")
            return redirect("account:profile_view")
    else:
        # GET: Điền sẵn các thông tin hiện tại vào Form để người dùng thấy
        form = CustomerForm(
            initial={
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "email": request.user.email,
                "phone": customer.phone,
            },
            instance=customer,
        )

    return render(
        request,
        "profile.html",
        {
            "form": form,
            "customer": customer,
            "active_section": "profile",
        },
    )


# Đổi mật khẩu cho người dùng đã đăng nhập (Yêu cầu mật khẩu cũ)
@login_required
def change_password(request: HttpRequest) -> HttpResponse:
    """Xác thực mật khẩu cũ và thiết lập mật khẩu mới một cách bảo mật."""
    form = PasswordChangeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        # Gọi Service xử lý đổi mật khẩu
        success, message = AccountService.change_password(
            request,
            request.user,
            form.cleaned_data["old_password"],
            form.cleaned_data["new_password"],
        )
        if success:
            messages.success(request, message)
            return redirect("account:profile_view")
        messages.error(request, message)

    return render(
        request,
        "registration/password_change_form.html",
        {
            "form": form,
            "customer": AccountService.get_or_create_customer(request.user),
        },
    )


# --- QUẢN LÝ ĐƠN HÀNG (ORDER HISTORY) ---

# Hiển thị lịch sử mua hàng của khách
@login_required
@customer_required
def purchase_list(request: HttpRequest) -> HttpResponse:
    """Hiển thị danh sách đơn hàng có tích hợp tìm kiếm, lọc trạng thái và phân trang."""
    customer = AccountService.get_or_create_customer(request.user)

    # Lấy các tham số lọc từ URL (GET params)
    query = request.GET.get("q", "")
    status = request.GET.get("status", "")

    # Sử dụng Selector để truy vấn dữ liệu từ Database theo bộ lọc
    orders_list = selectors.get_filtered_purchases(request.user, query, status)

    # Cấu hình phân trang: 5 đơn hàng mỗi lần xem
    paginator = Paginator(orders_list, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Lấy danh sách các trạng thái đơn hàng để hiển thị vào bộ lọc (Dropdown)
    status_choices = Order.STATUS_CHOICES

    return render(
        request,
        "purchase_list.html",
        {
            "orders": page_obj,
            "customer": customer,
            "active_section": "orders",
            "status_choices": status_choices,
            "query": query,
            "current_status": status,
        },
    )


# Chi tiết 1 đơn hàng — hiển thị khác nhau tùy vai trò (admin/staff/khách)
@login_required
def purchase_detail(request: HttpRequest, pk: int) -> HttpResponse:
    # 1. Khởi tạo dữ liệu cơ bản
    customer = AccountService.get_or_create_customer(request.user)
    # Tối ưu truy vấn sản phẩm trong đơn hàng
    items_qs = OrderItem.objects.select_related("product").all()

    # 2. PHÂN QUYỀN TRUY CẬP:
    # - Nếu là Nhân viên (is_staff): Được phép xem bất kỳ đơn hàng nào theo ID.
    # - Nếu là Khách thường: Chỉ được xem đơn hàng nếu đơn đó thuộc về chính mình (customer=request.user).
    if request.user.is_staff:
        order_filter = Q(id=pk)
    else:
        order_filter = Q(id=pk, customer=request.user)

    # 3. TỐI ƯU CƠ SỞ DỮ LIỆU:
    # - select_related: Gộp bảng (JOIN) để lấy thông tin Khách và Nhân viên xử lý trong 1 câu lệnh SQL.
    # - prefetch_related: Lấy trước danh sách các món hàng (OrderItem) để tránh lỗi N+1 query.
    order = get_object_or_404(
        Order.objects.select_related("customer", "assigned_staff").prefetch_related(
            Prefetch("items", queryset=items_qs)
        ),
        order_filter,
    )

    # 4. THIẾT LẬP CHẾ ĐỘ HIỂN THỊ (view_type):
    # Biến này sẽ được gửi xuống Template để quyết định xem có hiện nút "Giao hàng", "Huỷ đơn" hay không.
    view_type = "customer" # Mặc định là chế độ khách hàng
    staff_list = []
    
    if request.user.is_superuser:
        view_type = "admin" # Chế độ Admin: Có toàn quyền (giao việc cho nhân viên khác)
        staff_list = User.objects.filter(is_staff=True)
    elif request.user.is_staff:
        view_type = "staff" # Chế độ Nhân viên: Chỉ có quyền cập nhật trạng thái đơn được giao

    # 5. RENDER TEMPLATE: Gửi tất cả nguyên liệu đã chuẩn bị xuống file HTML
    return render(
        request,
        "purchase_detail.html",
        {
            "order": order,
            "items": order.items.all(),
            "customer": customer,
            "active_section": "orders",
            "view_type": view_type,  # <--- Biến quan trọng để phân biệt giao diện
            "staff_list": staff_list,
            "cancel_form": CancelOrderForm(),
        },
    )


# Xử lý yêu cầu hủy đơn hàng từ phía khách hàng
@login_required
@customer_required
def cancel_order(request: HttpRequest, pk: int) -> HttpResponse:
    """Khách hàng chỉ có quyền hủy đơn khi đơn chưa được xử lý xong (Pending/Processing)."""
    customer = AccountService.get_or_create_customer(request.user)
    
    # Bảo mật: Đảm bảo khách chỉ tìm thấy đúng đơn hàng của mình để hủy
    if request.user.is_staff:
        order_filter = Q(id=pk)
    else:
        order_filter = Q(id=pk, customer=request.user)

    order = get_object_or_404(Order, order_filter)

    # Kiểm tra quy định kinh doanh: Trạng thái nào thì không được hủy nữa?
    if order.status not in ["pending", "processing"]:
        messages.error(request, "Đơn hàng đã được xử lý sâu, không thể hủy vào lúc này.")
        return redirect("account:purchase_detail", pk=pk)

    # Xử lý Form hủy đơn (Yêu cầu khách nhập lý do)
    form = CancelOrderForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        # Gọi Service để thực hiện các bước hủy (Đổi trạng thái DB, hoàn kho, gửi mail...)
        success, message = AccountService.cancel_order(
            order, form.cleaned_data["cancel_reason"], user=request.user
        )
        if success:
            messages.success(request, message)
            return redirect("account:purchase_detail", pk=pk)
        messages.error(request, message)
        return redirect("account:purchase_detail", pk=pk)

    return render(
        request,
        "cancel_order.html",
        {
            "form": form,
            "order": order,
            "customer": customer,
            "active_section": "orders",
        },
    )


# Đăng ký tài khoản mới cho khách hàng
def signup(request: HttpRequest) -> HttpResponse:
    # 1. KHỞI TẠO FORM:
    # - Nếu người dùng gửi dữ liệu (POST): Nạp dữ liệu vào Form để kiểm tra.
    # - Nếu người dùng mới vào trang (GET): Tạo một Form trống.
    form = RegistrationForm(request.POST or None)

    # 2. XỬ LÝ DỮ LIỆU KHI BẤM NÚT ĐĂNG KÝ (POST):
    # Đây chính là phần thay thế cho thuộc tính 'action' trong HTML.
    if request.method == "POST" and form.is_valid():
        try:
            # Gọi Service để thực hiện nghiệp vụ đăng ký (Tạo User, tạo Profile...)
            AccountService.register_user(form.cleaned_data)

            messages.success(
                request, "Đăng ký tài khoản thành công. Vui lòng đăng nhập."
            )
            # Đăng ký xong thì chuyển hướng sang trang Đăng nhập
            return redirect("login")
        except Exception as e:
            # Nếu có lỗi (ví dụ: SĐT đã tồn tại), hiển thị thông báo lỗi
            messages.error(request, f"Đã xảy ra lỗi: {str(e)}")

    # 3. HIỂN THỊ GIAO DIỆN:
    # - Nếu là GET: Hiển thị trang đăng ký lần đầu.
    # - Nếu là POST nhưng nhập sai (form.is_valid() trả về False): 
    #   Django sẽ tự động giữ lại các giá trị đã nhập và đính kèm thông báo lỗi vào biến 'form' để hiển thị lại.
    return render(request, "registration/signup.html", {"form": form})
