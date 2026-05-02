from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse

from apps.core.decorators import admin_required
from apps.core.utils import get_paginated_data
from .models import Promotion
from .forms import PromotionForm
from .selectors import PromotionSelector
from .services import PromotionService


@login_required
@admin_required
def promotion_list(request):
    query = request.GET.get("q", "")
    status = request.GET.get("status", "")

    stats = PromotionSelector.get_promotion_stats()

    promotions_list = PromotionSelector.get_filtered_promotions(
        query=query, status=status
    )

    page_obj = get_paginated_data(promotions_list, request, 10)

    context = {"page_obj": page_obj, **stats}
    return render(request, "promotion_list.html", context)


@login_required
@admin_required
def add_promotion(request, pk=None):
    promotion = get_object_or_404(Promotion, pk=pk) if pk else None

    if request.method == "POST":
        form = PromotionForm(request.POST, request.FILES, instance=promotion)
        if form.is_valid():
            saved_promo = form.save()

            PromotionService.send_promotion_notifications(saved_promo)

            messages.success(
                request,
                f'Đã {"cập nhật" if pk else "thêm mới"} chương trình khuyến mãi thành công!',
            )
            return redirect("promotions:promotion_list")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = PromotionForm(instance=promotion)

    return render(
        request, "add_promotion.html", {"form": form, "is_edit": pk is not None}
    )


@login_required
@admin_required
def promotion_detail(request, pk):
    promotion = get_object_or_404(Promotion, pk=pk)
    return render(request, "promotion_detail.html", {"promotion": promotion})


@login_required
@admin_required
def delete_promotion(request, pk):
    promotion = get_object_or_404(Promotion, pk=pk)
    if request.method == "POST":
        name = promotion.name
        promotion.delete()
        messages.success(
            request, f'Đã xóa chương trình khuyến mãi "{name}" thành công.'
        )
    return redirect("promotions:promotion_list")


def api_promotion_detail(request, pk):
    promotion = get_object_or_404(Promotion, pk=pk)

    products_data = [
        {
            "name": p.name,
            "id": p.id,
            "image": p.image.url if p.image else "/static/img/product-placeholder.png",
            "price": f"{p.price:,.0f}đ",
            "url": reverse("core:view_product_detail", args=[p.slug]),
        }
        for p in promotion.products.all()
    ]

    discount_display = (
        f"{promotion.value:,.0f}%"
        if promotion.discount_type == "percent"
        else f"{promotion.value:,.0f}đ"
    )

    return JsonResponse(
        {
            "status": "success",
            "name": promotion.name,
            "code": promotion.code,
            "discount_display": discount_display,
            "description": getattr(
                promotion,
                "description",
                "Ưu đãi đặc biệt cho dòng sản phẩm của Dahuka.",
            ),
            "condition": f"{promotion.condition:,.0f}",
            "products": products_data,
        }
    )
