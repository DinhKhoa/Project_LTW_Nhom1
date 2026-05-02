from django.http import JsonResponse, Http404, HttpRequest, HttpResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from apps.products.models import Product
from apps.orders.models import Order
from apps.account.decorators import customer_required
from apps.account.services import AccountService
from apps.core.utils import format_money
from apps.core.constants import DEFAULT_DELIVERY_DAYS
from .models import CartItem
from .forms import CustomerInfoForm
from .services import CartService
from . import selectors


def cart(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated and request.user.is_staff:
        raise Http404

    cart_obj = CartService.get_or_create_cart(request)
    state = CartService.get_checkout_state(request)

    if request.method == "GET":
        referer = request.META.get("HTTP_REFERER", "")
        cart_url = request.build_absolute_uri(reverse("cart:cart")).split("?")[0]
        checkout_url = request.build_absolute_uri(reverse("cart:checkout")).split("?")[0]
        if referer and not referer.startswith(cart_url) and not referer.startswith(checkout_url):
            if request.GET.get("buy_now") != "1": state["selected_ids"] = []
            state["current_screen"] = "cart"
            request.session.modified = True

    state["current_screen"] = "cart"
    request.session.modified = True

    if request.method == "POST":
        action = request.POST.get("action")
        is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"
        
        CartService.handle_cart_action(request, cart_obj, state)
        
        if action == "bulk_delete":
            messages.success(request, "Đã xóa các sản phẩm đã chọn")
        elif action == "go_to_order":
            if not state["selected_ids"]:
                messages.error(request, "Chưa chọn sản phẩm để thanh toán")
                return redirect(reverse("cart:cart"))
            state["current_screen"] = "order"
            request.session.modified = True
            return redirect(reverse("cart:checkout"))

        if is_ajax:
            return JsonResponse({"ok": True, **CartService.get_ajax_payload(cart_obj, state)})
        return redirect(request.path)

    cart_items = selectors.get_cart_items(cart_obj)
    for item in cart_items:
        if item.price != item.product.price:
            item.price = item.product.price
            item.save()
        item.is_selected = item.id in state["selected_ids"]

    totals = CartService.get_cart_totals(cart_obj, state, apply_promos=False)
    context = {
        "cart": cart_obj, "cart_items": cart_items, "total_price": totals["total_price"],
        "discount_amount": totals["discount_amount"], "formatted_discount_amount": format_money(totals["discount_amount"]),
        "final_total": totals["final_total"], "formatted_total_price": format_money(totals["final_total"]),
        "formatted_deposit_amount": format_money(totals["deposit_amount"]), "state": state,
        "current_screen": "cart", "display_title": "Giỏ hàng",
        "breadcrumbs": [{"name": "Trang chủ", "url": "/"}, {"name": "Giỏ hàng", "url": None}],
    }
    return render(request, "cart.html", context)


def checkout(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated and request.user.is_staff:
        raise Http404

    cart_obj = CartService.get_or_create_cart(request)
    state = CartService.get_checkout_state(request)

    if not state["selected_ids"] and state.get("current_screen") != "success":
        messages.warning(request, "Vui lòng chọn sản phẩm trước khi thanh toán")
        return redirect(reverse("cart:cart"))

    if state.get("current_screen") == "cart":
        state["current_screen"] = "order"
        request.session.modified = True

    if request.method == "POST":
        action = request.POST.get("action")
        is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"

        if action == "update_customer":
            customer_data = {
                "full_name": request.POST.get("full_name"), "phone": request.POST.get("phone"),
                "province": request.POST.get("province"), "district": request.POST.get("district"),
                "ward": request.POST.get("ward"), "address_detail": request.POST.get("address_detail"),
                "address_type": request.POST.get("address_type", "home"),
                "is_default": request.POST.get("is_default") == "on",
            }
            state["customer"].update(customer_data)
            if request.user.is_authenticated:
                addr_id = request.POST.get("id")
                if addr_id:
                    addr = AccountService.update_address(request.user.customer, addr_id, customer_data)
                    state["customer"]["id"] = addr.id
                    messages.success(request, "Đã cập nhật địa chỉ")
                else:
                    addr = AccountService.create_address(request.user.customer, customer_data)
                    state["customer"]["id"] = addr.id
                    messages.success(request, "Đã thêm địa chỉ mới")
            else:
                messages.success(request, "Đã cập nhật thông tin nhận hàng")
            request.session.modified = True
            return redirect(request.path)

        elif action == "select_saved_address":
            if request.user.is_authenticated:
                addr = get_object_or_404(request.user.customer.addresses, id=request.POST.get("address_id"))
                state["customer"].update({
                    "full_name": addr.full_name, "phone": addr.phone, "province": addr.province,
                    "district": addr.district, "ward": addr.ward, "address_detail": addr.address_detail,
                    "address_type": addr.address_type, "is_default": addr.is_default, "id": addr.id,
                })
                request.session.modified = True
                messages.success(request, "Đã chọn địa chỉ giao hàng")
                return redirect(request.path)

        elif action == "delete_saved_address":
            if request.user.is_authenticated:
                AccountService.delete_address(request.user.customer, request.POST.get("address_id"))
                messages.success(request, "Đã xóa địa chỉ")
                return redirect(request.path)

        elif action == "apply_coupon":
            code = request.POST.get("coupon_code", "").strip().upper()
            if CartService.apply_promotion(code, float(cart_obj.selected_total_price)) > 0:
                state["coupon_code"] = code
                messages.success(request, f"Áp dụng mã {code} thành công!")
            else:
                state["coupon_code"] = ""
                messages.error(request, "Mã giảm giá không hợp lệ.")
            request.session.modified = True
            return redirect(reverse("cart:checkout"))

        elif action == "submit_order":
            if not state["customer"].get("full_name") or not state["customer"].get("phone"):
                messages.warning(request, "Vui lòng nhập thông tin nhận hàng")
                return redirect(reverse("cart:checkout"))
            state["current_screen"] = "bank_payment"
            state["order_note"] = request.POST.get("note", "").strip()
            request.session.modified = True
            return redirect(reverse("cart:checkout"))

        elif action == "confirm_bank_payment":
            selected_items = cart_obj.items.filter(id__in=state["selected_ids"])
            try:
                totals = CartService.get_cart_totals(cart_obj, state)
                order = CartService.create_order_from_cart(
                    user=request.user if request.user.is_authenticated else None,
                    cart_obj=cart_obj, customer_data=state["customer"],
                    order_items_data=[{"product_id": i.product.id, "quantity": i.quantity, "price": i.price} for i in selected_items],
                    payment_type=state.get("cart_payment_type", "full"),
                    deposit_amount=totals["deposit_amount"], note=state.get("order_note", ""),
                )
                selected_items.delete()
                state.update({"selected_ids": [], "current_screen": "success", "last_order_code": order.order_code})
                request.session.pop("order_note", None)
                request.session.modified = True
                return redirect(reverse("cart:checkout"))
            except Exception as e:
                messages.error(request, str(e))
                return redirect(reverse("cart:checkout"))

        CartService.handle_cart_action(request, cart_obj, state)
        if is_ajax: return JsonResponse({"ok": True, **CartService.get_ajax_payload(cart_obj, state)})

    cart_items = selectors.get_cart_items(cart_obj, selected_ids=state["selected_ids"])
    totals = CartService.get_cart_totals(cart_obj, state)
    customer_form = CustomerInfoForm(initial={**state["customer"]})
    full_address = ", ".join([p for p in [state["customer"].get("address_detail"), state["customer"].get("ward"), state["customer"].get("district"), state["customer"].get("province")] if p])

    context = {
        "cart": cart_obj, "cart_items": cart_items, "total_price": totals["total_price"],
        "shipping_fee": totals["shipping_fee"], "discount_amount": totals["discount_amount"],
        "formatted_discount_amount": format_money(totals["discount_amount"]), "final_total": totals["final_total"],
        "formatted_total_price": format_money(totals["final_total"]), "deposit_amount": totals["deposit_amount"],
        "formatted_deposit_amount": format_money(totals["deposit_amount"]), "formatted_remaining_amount": format_money(totals["final_total"] - totals["deposit_amount"]),
        "deposit_percent": totals["deposit_percent"], "applied_promotions": totals["applied_promotions"],
        "state": state, "current_screen": state["current_screen"], "display_title": "Xác nhận đơn hàng",
        "breadcrumbs": [{"name": "Trang chủ", "url": "/"}, {"name": "Thanh toán", "url": None}],
        "customer_full_address": full_address, "customer_formatted_phone": f"(+84) {state['customer']['phone']}" if state["customer"]["phone"] else "",
        "customer_form": customer_form, "addresses": request.user.customer.addresses.all() if request.user.is_authenticated else [],
        "delivery_date": (timezone.localtime() + timezone.timedelta(days=DEFAULT_DELIVERY_DAYS)).strftime("%d/%m"),
    }
    return render(request, "checkout.html", context)


@require_POST
def add_product_to_cart(request: HttpRequest) -> HttpResponse:
    product = get_object_or_404(Product, id=request.POST.get("product_id"))
    cart_obj = CartService.get_or_create_cart(request)
    item = CartService.add_to_cart(cart_obj, product, int(request.POST.get("quantity", 1)))

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"status": "success", "message": f"Đã thêm {product.name} vào giỏ hàng", "cart_count": cart_obj.items.count()})

    if request.POST.get("action") == "buy_now":
        state = CartService.get_checkout_state(request)
        state["selected_ids"] = [item.id]
        request.session.modified = True
        return redirect(reverse("cart:cart") + "?buy_now=1")

    messages.success(request, f"Đã thêm {product.name} vào giỏ hàng")
    return redirect(reverse("cart:cart"))


@login_required
@customer_required
def reorder_view(request: HttpRequest, order_id: int) -> HttpResponse:
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    cart_obj = CartService.get_or_create_cart(request)
    item_ids = CartService.reorder(cart_obj, order)
    state = CartService.get_checkout_state(request)
    state.update({"selected_ids": item_ids, "current_screen": "cart"})
    request.session.modified = True
    messages.success(request, f"Đã thêm các sản phẩm từ đơn {order.order_code} vào giỏ hàng.")
    return redirect(reverse("cart:cart") + "?buy_now=1")


@require_POST
def delete_cart_item(request: HttpRequest, item_id: int) -> HttpResponse:
    cart_obj = CartService.get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart_obj)
    state = CartService.get_checkout_state(request)
    if item_id in state.get("selected_ids", []): state["selected_ids"].remove(item_id)
    request.session.modified = True
    item.delete()
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"ok": True, **CartService.get_ajax_payload(cart_obj, state)})
    messages.success(request, "Đã xóa sản phẩm khỏi giỏ hàng")
    return redirect(reverse("cart:cart"))
