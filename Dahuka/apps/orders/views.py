from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.core.decorators import admin_required, staff_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import Http404, HttpRequest, HttpResponse

from .models import Order
from .services import OrderService
from . import selectors


# ==============================================================================
# VIEW: DANH SÁCH ĐƠN HÀNG (Dành cho Quản trị)
# ==============================================================================
@login_required
@admin_required
def order_list(request: HttpRequest) -> HttpResponse:
    """
    Hiển thị danh sách đơn hàng toàn hệ thống.
    Hỗ trợ: Tìm kiếm theo từ khóa, Lọc theo trạng thái, Phân trang và Thống kê nhanh.
    """
    # 1. Lấy các tham số lọc từ URL (VD: ?q=DHK&trang_thai=pending&page=2)
    query = request.GET.get("q", "")
    trang_thai_filter = request.GET.get("trang_thai", "")
    page_number = int(request.GET.get("page", 1))

    # 2. Gọi SELECTOR để xử lý truy vấn phức tạp (lọc + phân trang)
    page_obj = selectors.get_paginated_orders(
        query=query,
        status_filter=trang_thai_filter,
        page_number=page_number,
        user=request.user,
    )

    # 3. Lấy số liệu thống kê để hiển thị các ô đếm (Top bar)
    stats = selectors.get_order_statistics()

    context = {
        "page_obj": page_obj,
        "query": query,
        "trang_thai_filter": trang_thai_filter,
        "trang_thai_choices": Order.STATUS_CHOICES, # Dùng cho Dropdown bộ lọc
        "stats": stats,
    }
    return render(request, "order_list.html", context)


# ==============================================================================
# VIEW: CHI TIẾT ĐƠN HÀNG & THAO TÁC XỬ LÝ (Cho phép Admin & Nhân viên phụ trách)
# ==============================================================================
@login_required
@staff_required
def order_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Hiển thị chi tiết 1 đơn hàng và tiếp nhận các hành động thay đổi trạng thái.
    Hành động bao gồm: Giao việc, Bắt đầu giao hàng, Hoàn thành, Hủy đơn.
    """
    try:
        # Lấy thông tin đơn hàng đã được tối ưu truy vấn (JOIN bảng)
        order = selectors.get_order_detail(pk=pk)
    except Order.DoesNotExist:
        raise Http404("Đơn hàng không tồn tại.")

    # KIỂM TRA QUYỀN TRUY CẬP CHI TIẾT:
    # 1. Admin (Superuser): Quyền tối cao, xem mọi đơn.
    # 2. Nhân viên (Staff): Chỉ xem được đơn mình được giao nhiệm vụ (assigned_staff).
    # 3. Khách hàng: Chỉ xem được đơn mình đã đặt.
    is_authorized = False
    if request.user.is_superuser:
        is_authorized = True
    elif request.user.is_staff:
        if order.assigned_staff == request.user:
            is_authorized = True
    elif order.customer == request.user:
        is_authorized = True

    if not is_authorized:
        raise Http404("Bạn không có quyền xem đơn hàng này.")

    # XỬ LÝ KHI NGƯỜI DÙNG BẤM NÚT (POST)
    if request.method == "POST":
        if not request.user.is_staff:
            messages.error(request, "Bạn không có quyền thực hiện thao tác này.")
            return redirect("orders:order_detail", pk=pk)

        # Đọc dữ liệu từ form gửi lên
        action = request.POST.get("action", "")
        staff_id = request.POST.get("assigned_staff", "")
        cancel_reason = request.POST.get("cancel_reason", "")
        proof_image = request.FILES.get("proof_image")

        # GỌI SERVICE để thực hiện thay đổi dữ liệu (Business Logic)
        OrderService.handle_order_action(
            order, action, staff_id, cancel_reason, proof_image, user=request.user
        )

        # HỖ TRỢ AJAX: Nếu gọi bằng JS, trả về kết quả dạng JSON để cập nhật UI mượt mà
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            from django.http import JsonResponse
            return JsonResponse({
                "status": "success",
                "message": "Cập nhật đơn hàng thành công.",
                "order_status": order.get_status_display(),
                "order_status_raw": order.status,
                "current_step": OrderService.calc_current_step(order),
            })

        # Trả về trang chi tiết bình thường nếu không dùng AJAX
        messages.success(request, "Cập nhật đơn hàng thành công.")
        return redirect("orders:order_detail", pk=pk)

    # --- PHẦN HIỂN THỊ (GET) ---
    # Xác định vai trò của người đang xem để hiển thị giao diện phù hợp
    view_type = "customer"
    if request.user.is_superuser:
        view_type = "admin"     # Admin: có quyền gán nhân viên
    elif request.user == order.assigned_staff:
        view_type = "staff"     # Staff: chỉ có quyền cập nhật tiến độ giao hàng

    context = {
        "order": order,
        "items": order.items.all(),
        "current_step": OrderService.calc_current_step(order), # 0-3 cho Progress Bar
        # Lấy danh sách nhân viên để Admin lựa chọn gán việc
        "staff_list": User.objects.filter(is_staff=True, is_superuser=False).select_related("customer"),
        "view_type": view_type,
    }
    return render(request, "order_detail.html", context)
