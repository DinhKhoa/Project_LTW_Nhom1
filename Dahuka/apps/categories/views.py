from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.contrib import messages

from apps.core.decorators import admin_required
from apps.core.utils import get_paginated_data
from apps.products.services import ProductsService

from .selectors import search_categories, get_category_by_id
from .services import CategoryService

# ==============================================================================
# VIEWS: ĐIỀU HƯỚNG VÀ XỬ LÝ YÊU CẦU (Controller Layer)
# ==============================================================================
# Các hàm View trong dự án Dahuka thực hiện các nhiệm vụ chính sau:
# 1. Tiếp nhận yêu cầu (Request) từ trình duyệt của người dùng.
# 2. Gọi các hàm Selector để truy vấn dữ liệu từ Database.
# 3. Gọi các hàm Service để thực hiện các logic nghiệp vụ (Thêm, Sửa, Xóa).
# 4. Trả về kết quả phản hồi (Render giao diện HTML hoặc Redirect trang).

@login_required
@admin_required
def category_list(request: HttpRequest) -> HttpResponse:
    """
    View hiển thị trang danh sách toàn bộ các danh mục sản phẩm.
    Hỗ trợ tính năng tìm kiếm theo từ khóa và phân trang tự động.
    """
    # Lấy từ khóa tìm kiếm người dùng nhập từ thanh URL (Ví dụ: ?q=may-loc-nuoc)
    query = request.GET.get("q", "")
    
    # 1. Sử dụng Selector để truy vấn danh sách danh mục (có lọc theo từ khóa nếu có)
    categories_qs = search_categories(query)
    
    # 2. Thực hiện phân trang dữ liệu (Sử dụng hàm tiện ích core, mặc định 10 mục/trang)
    page_obj = get_paginated_data(categories_qs, request, 10)

    # 3. Trả về giao diện template 'categories_list.html' kèm theo các dữ liệu đã xử lý
    return render(request, "categories_list.html", {
        "page_obj": page_obj,
        "query": query,
    })

@login_required
@admin_required
def category_add(request: HttpRequest) -> HttpResponse:
    """
    Xử lý yêu cầu thêm mới một danh mục sản phẩm vào hệ thống.
    Dữ liệu được gửi lên thông qua phương thức POST từ Modal trên giao diện quản trị.
    """
    if request.method == "POST":
        # Gọi Service Layer để xử lý việc kiểm tra tính hợp lệ (Validation) và lưu DB
        success, category, errors = CategoryService.create_category(request.POST, request.FILES)
        
        if success:
            # Nếu lưu thành công, tạo thông báo xanh (Success) để hiển thị trên web
            messages.success(request, f'Đã thêm danh mục "{category.name}" thành công.')
        else:
            # Nếu có lỗi (Ví dụ: trùng tên), duyệt qua danh sách lỗi và hiển thị thông báo đỏ (Error)
            for field, field_errors in errors.items():
                for error in field_errors:
                    messages.error(request, f"{field}: {error}")
    
    # Sau khi xử lý xong (dù thành hay bại), luôn quay lại trang danh sách danh mục
    return redirect("categories:category_list")

@login_required
@admin_required
def category_edit(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Xử lý yêu cầu chỉnh sửa thông tin cho một danh mục đã tồn tại.
    Dữ liệu nhận được từ Form chỉnh sửa (Modal Edit).
    """
    # 1. Tìm đối tượng danh mục cần sửa dựa trên Primary Key (pk)
    category = get_category_by_id(pk)
    
    if request.method == "POST":
        # 2. Gọi Service để thực hiện cập nhật các thay đổi vào Database
        success, category, errors = CategoryService.update_category(category, request.POST, request.FILES)
        
        if success:
            messages.success(request, f'Đã cập nhật danh mục "{category.name}" thành công.')
        else:
            for field, field_errors in errors.items():
                for error in field_errors:
                    messages.error(request, f"{field}: {error}")
                    
    return redirect("categories:category_list")

@login_required
@admin_required
def category_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Xử lý yêu cầu xóa vĩnh viễn một danh mục.
    Chỉ chấp nhận phương thức POST (nhấn từ Modal xác nhận) để đảm bảo an toàn dữ liệu.
    """
    if request.method == "POST":
        # 1. Lấy thông tin danh mục cần thực thi lệnh xóa
        category = get_category_by_id(pk)
        
        # 2. Gọi Service để thực hiện lệnh xóa và nhận lại tên danh mục đã xóa
        success, name = CategoryService.delete_category(category)
        
        if success:
            messages.success(request, f'Đã xóa danh mục "{name}" thành công.')
            
    return redirect("categories:category_list")

@login_required
@admin_required
def get_category_products(request: HttpRequest, pk: int) -> JsonResponse:
    """
    View hỗ trợ lấy nhanh danh sách sản phẩm thuộc một danh mục cụ thể (Dạng AJAX).
    Kết quả trả về định dạng JSON để Javascript bên ngoài có thể xử lý hiển thị linh hoạt.
    """
    # 1. Tìm đối tượng danh mục tương ứng
    category = get_category_by_id(pk)
    
    # 2. Gọi Service của app Products để chuyển đổi dữ liệu sản phẩm sang định dạng phù hợp
    products = ProductsService.format_products_for_dropdown(category)
    
    # 3. Trả về kết quả JSON cho trình duyệt
    return JsonResponse({"products": products})
