import json
from typing import Any, Dict
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_POST
from django.contrib import messages

from apps.core.utils import get_paginated_data
from apps.core.decorators import admin_required
from apps.categories.models import Category
from .models import ProductImage
from .forms import ProductForm
from .services import ProductsService
from . import selectors


# Danh sách sản phẩm dành cho Admin — có tìm kiếm, lọc theo danh mục và tồn kho
# Chỉ Admin mới được truy cập (decorator @admin_required kiểm tra)
@login_required
@admin_required
def product_list(request: HttpRequest) -> HttpResponse:
    # request.GET.get('key', 'default'): Lấy tham số từ URL (?q=...&category=...).
    query = request.GET.get("q", "")
    category_id = request.GET.get("category", "all")
    inventory_filter = request.GET.get("inventory", "default")

    # Gọi selector để lấy danh sách sản phẩm đã lọc từ DB
    products_list = selectors.get_filtered_products(
        query=query, category_id=category_id, inventory_filter=inventory_filter
    )

    # Phân trang: 10 sản phẩm mỗi trang
    page_obj = get_paginated_data(products_list, request, 10)
    categories = Category.objects.all()

    context = {
        "page_obj": page_obj,
        "categories": categories,
        "query": query,
        "category_id": category_id,
        "inventory_filter": inventory_filter,
    }
    return render(request, "product_list.html", context)


# Trang thêm mới / chỉnh sửa sản phẩm — dùng chung 1 view
# pk=None → mode "create" (thêm mới); pk có giá trị → mode "update" (sửa)
@login_required
@admin_required
def product_detail(request: HttpRequest, pk: int = None) -> HttpResponse:
    product = selectors.get_product_by_id(pk) if pk else None
    mode = "update" if pk else "create"

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            # commit=False: Tạo đối tượng sản phẩm từ Form nhưng chưa lưu xuống DB ngay.
            # Điều này giúp chúng ta có thể sửa đổi thêm thuộc tính trước khi lưu chính thức.
            saved_product = form.save(commit=False)

            # Xử lý xóa ảnh thủ công nếu có yêu cầu
            for field in ["image", "image_features", "image_description"]:
                if request.POST.get(f"{field}-clear") == "on":
                    setattr(saved_product, field, None)

            saved_product.save()  # Lưu chính thức vào DB để lấy ID

            # save_m2m(): Bắt buộc gọi khi dùng commit=False.
            # Nó giúp lưu các quan hệ "Nhiều-Nhiều" (như Tags) vào bảng trung gian sau khi sản phẩm đã có ID.
            form.save_m2m()

            # Xóa các ảnh gallery được đánh dấu xóa (từ JS gửi lên danh sách ID)
            delete_ids = request.POST.get("delete_image_ids", "").split(",")
            for img_id in delete_ids:
                if img_id.isdigit():
                    ProductImage.objects.filter(
                        id=img_id, product=saved_product
                    ).delete()

            # Xử lý upload ảnh gallery mới từ request.FILES
            ProductsService.handle_product_images(saved_product, request.FILES)
            messages.success(
                request, f'Đã {"cập nhật" if pk else "thêm mới"} sản phẩm thành công!'
            )
            return redirect("products:product_detail", pk=saved_product.pk)

        messages.error(
            request, "Không thể lưu sản phẩm. Vui lòng kiểm tra lại các trường đã nhập."
        )
    else:
        # GET: hiển thị form trống (thêm mới) hoặc form điền sẵn (sửa)
        form = ProductForm(instance=product)

    images_by_type: Dict[str, Any] = {}
    if product:
        images_by_type["gallery"] = product.images.all()

    context = {
        "product": product,
        "form": form,
        "categories": Category.objects.all(),
        "mode": mode,
        "images_by_type": images_by_type,
    }
    return render(request, "product_detail.html", context)


# Bật/tắt hiển thị sản phẩm (ẩn/hiện) — gọi qua AJAX từ trang danh sách
# @require_POST: chỉ chấp nhận POST request, từ chối GET
@login_required
@admin_required
@require_POST
def toggle_product_visibility(request: HttpRequest, pk: int) -> JsonResponse:
    try:
        product = selectors.get_product_by_id(pk)
        data = json.loads(request.body)
        is_visible = data.get("is_visible", True)
        # Gọi service để cập nhật is_active của sản phẩm
        new_status = ProductsService.toggle_visibility(product, is_visible)
        return JsonResponse({"status": "success", "is_active": new_status})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


# Xóa 1 ảnh gallery của sản phẩm — gọi qua AJAX từ trang chi tiết sản phẩm
@login_required
@admin_required
@require_POST
def delete_product_image(request: HttpRequest, img_id: int) -> JsonResponse:
    try:
        image = ProductImage.objects.get(id=img_id)
        image.delete()
        return JsonResponse({"status": "success", "message": "Đã xóa ảnh thành công"})
    except ProductImage.DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": "Không tìm thấy ảnh"}, status=404
        )
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)
