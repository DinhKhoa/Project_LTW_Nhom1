from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from apps.products.models import Product
from apps.account.models import Customer, Address
from apps.orders.services import OrderService
from .models import Cart, CartItem
from .forms import CustomerInfoForm
from .services import CartService
from apps.core.constants import (
    DEFAULT_DELIVERY_CITY,
    DEFAULT_DELIVERY_DAYS,
    CART_DEFAULT_DEPOSIT_PERCENT,
    CART_MIN_DEPOSIT_PERCENT,
    CART_MAX_DEPOSIT_PERCENT,
)
from apps.promotions.models import Promotion
from django.utils import timezone


# Helper function for formatting money
def format_money(value):
    if value is None:
        return "0"
    return "{:,.0f}".format(value).replace(",", ".")


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


def cart(request):
    if request.user.is_authenticated and request.user.is_staff:
        raise Http404

    cart_obj = get_or_create_cart(request)

    if "checkout_state" not in request.session:
        customer_data = {
            "name": "",
            "phone": "",
            "email": "",
            "city": DEFAULT_DELIVERY_CITY,
            "district": "",
            "ward": "",
            "street": "",
        }

        if request.user.is_authenticated:
            try:
                profile = request.user.customer
                customer_data["name"] = (request.user.get_full_name() or request.user.username)
                customer_data["phone"] = profile.phone
                customer_data["email"] = request.user.email
                default_addr = profile.addresses.filter(is_default=True).first() or profile.addresses.first()
                if default_addr:
                    customer_data["name"] = default_addr.full_name
                    customer_data["phone"] = default_addr.phone
                    customer_data["city"] = default_addr.province
                    customer_data["district"] = default_addr.district
                    customer_data["ward"] = default_addr.ward
                    customer_data["street"] = default_addr.address_detail
            except Exception: pass

        request.session["checkout_state"] = {
            "current_screen": "cart",
            "cart_payment_type": "full",
            "order_method": "bank",
            "deposit_percent": CART_DEFAULT_DEPOSIT_PERCENT,
            "coupon_code": "",
            "customer": customer_data,
        }

    state = request.session["checkout_state"]
    current_screen = state.get("current_screen", "cart")

    page_titles = {
        "cart": "Giỏ hàng",
        "order": "Xác nhận đơn hàng",
        "bank_payment": "Thanh toán chuyển khoản",
        "success": "Đặt hàng thành công",
    }
    display_title = page_titles.get(current_screen, "Giỏ hàng")
    breadcrumbs = [{"name": "Trang chủ", "url": "/"}, {"name": display_title, "url": None}]

    if request.method == "GET":
        referer = request.META.get("HTTP_REFERER", "")
        cart_url = request.build_absolute_uri(reverse("cart:cart"))
        if not referer or not referer.startswith(cart_url.split("?")[0]):
            state["current_screen"] = "cart"
            request.session.modified = True
            current_screen = "cart"

    cart_items = cart_obj.items.all().select_related("product") if current_screen == "cart" else cart_obj.items.filter(is_selected=True).select_related("product")
    
    total_price = cart_obj.selected_total_price
    shipping_fee = 0
    
    # Promotion Logic
    discount_amount = 0
    if state.get("coupon_code"):
        promo = Promotion.objects.filter(code__iexact=state["coupon_code"], is_active=True, start_date__lte=timezone.now().date(), end_date__gte=timezone.now().date()).first()
        if promo:
            discount_amount = promo.calculate_discount(total_price)
        else:
            state["coupon_code"] = ""
            request.session.modified = True

    final_total = float(total_price) + shipping_fee - float(discount_amount)
    if final_total < 0: final_total = 0
    
    deposit_amount = round(final_total * state["deposit_percent"] / 100)

    def checkout_payload():
        return {
            "cart_payment_type": state["cart_payment_type"],
            "order_method": state["order_method"],
            "deposit_percent": state["deposit_percent"],
            "formatted_deposit_amount": format_money(deposit_amount),
            "formatted_total_price": format_money(final_total),
            "discount_amount": format_money(discount_amount),
            "coupon_code": state.get("coupon_code", ""),
        }

    from .forms import CustomerInfoForm
    customer_form = CustomerInfoForm(initial={
        "customer_name": state["customer"].get("name", ""),
        "customer_phone": state["customer"].get("phone", ""),
        "customer_email": state["customer"].get("email", ""),
        "customer_city": state["customer"].get("city", ""),
        "customer_district": state["customer"].get("district", ""),
        "customer_ward": state["customer"].get("ward", ""),
        "customer_street": state["customer"].get("street", ""),
        "customer_note": state["customer"].get("note", ""),
    })

    if request.method == "POST":
        action = request.POST.get("action")
        is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"

        if action == "update_customer":
            form = CustomerInfoForm(request.POST)
            if form.is_valid():
                state["customer"].update({
                    "name": form.cleaned_data["customer_name"],
                    "phone": form.cleaned_data["customer_phone"],
                    "email": form.cleaned_data["customer_email"],
                    "city": form.cleaned_data["customer_city"],
                    "district": form.cleaned_data["customer_district"],
                    "ward": form.cleaned_data["customer_ward"],
                    "street": form.cleaned_data["customer_street"],
                    "note": form.cleaned_data["customer_note"],
                })
                request.session.modified = True
                messages.success(request, "Cập nhật tin nhận hàng thành công")
                return redirect(reverse("cart:cart"))

        elif action == "toggle_select":
            item = get_object_or_404(CartItem, id=request.POST.get("item_id"), cart=cart_obj)
            item.is_selected = request.POST.get("is_selected") == "true"
            item.save()
            if is_ajax: return JsonResponse({"ok": True, **checkout_payload()})
            return redirect(reverse("cart:cart"))

        elif action == "update_quantity":
            item = get_object_or_404(CartItem, id=request.POST.get("item_id"), cart=cart_obj)
            try:
                quantity = int(request.POST.get("quantity", 1))
                if quantity >= 1:
                    item.quantity = quantity
                    item.save()
            except (TypeError, ValueError):
                pass
            if is_ajax: return JsonResponse({"ok": True, **checkout_payload()})
            return redirect(reverse("cart:cart"))

        elif action == "update_payment_type":
            state["cart_payment_type"] = request.POST.get("cart_payment_type")
            if state["cart_payment_type"] == "full": state["order_method"] = "bank"
            request.session.modified = True
            if is_ajax: return JsonResponse({"ok": True, **checkout_payload()})
            return redirect(reverse("cart:cart"))

        elif action == "apply_coupon":
            code = request.POST.get("coupon_code", "").strip().upper()
            promo = Promotion.objects.filter(code__iexact=code, is_active=True, start_date__lte=timezone.now().date(), end_date__gte=timezone.now().date()).first()
            if promo:
                state["coupon_code"] = code
                messages.success(request, f"Áp dụng mã {code} thành công!")
            else:
                state["coupon_code"] = ""
                messages.error(request, "Mã giảm giá không hợp lệ.")
            request.session.modified = True
            return redirect(reverse("cart:cart"))

        elif action == "go_to_order":
            if not state["customer"]["name"] or not state["customer"]["phone"]:
                messages.warning(request, "Vui lòng nhập thông tin nhận hàng")
                return redirect(reverse("cart:cart"))
            state["current_screen"] = "order"
            request.session.modified = True
            return redirect(reverse("cart:cart"))

        elif action == "submit_order":
            selected_items = cart_obj.items.filter(is_selected=True)
            if not selected_items.exists():
                messages.error(request, "Chưa chọn sản phẩm.")
                return redirect(reverse("cart:cart"))

            try:
                order = CartService.create_order_from_cart(
                    user=request.user if request.user.is_authenticated else None,
                    cart_obj=cart_obj,
                    customer_data=state["customer"],
                    order_items_data=[{"product_id": i.product.id, "quantity": i.quantity, "price": i.price} for i in selected_items],
                    coupon_code=state.get("coupon_code"),
                    payment_type=state.get("cart_payment_type", "full"),
                    order_method=state.get("order_method", "bank")
                )
                selected_items.delete()
                
                # Navigate to next screen
                if (state["order_method"] == "bank" or state["cart_payment_type"] == "deposit"):
                    state["current_screen"] = "bank_payment"
                else:
                    state["current_screen"] = "success"
                
                request.session.modified = True
            except Exception as e:
                messages.error(request, str(e))
            return redirect(reverse("cart:cart"))

        elif action in ("go_home_again", "shop_again"):
            state["current_screen"] = "cart"
            request.session.modified = True
            return redirect(reverse("cart:cart"))

        elif action == "confirm_bank_payment":
            state["current_screen"] = "success"
            request.session.modified = True
            return redirect(reverse("cart:cart"))

    context = {
        "cart": cart_obj, "cart_items": cart_items, 
        "total_price": total_price, "shipping_fee": shipping_fee,
        "discount_amount": discount_amount, "formatted_discount_amount": format_money(discount_amount),
        "final_total": final_total, "formatted_total_price": format_money(final_total),
        "deposit_amount": deposit_amount, "formatted_deposit_amount": format_money(deposit_amount),
        "formatted_remaining_amount": format_money(final_total - deposit_amount),
        "state": state, "current_screen": current_screen, "display_title": display_title, "breadcrumbs": breadcrumbs,
        "customer_full_address": ", ".join([p for p in [state['customer'].get('street'), state['customer'].get('ward'), state['customer'].get('district'), state['customer'].get('city')] if p]),
        "customer_formatted_phone": f"(+84) {state['customer']['phone']}" if state['customer']['phone'] else "",
        "customer_form": customer_form, "delivery_date": (timezone.now() + timezone.timedelta(days=DEFAULT_DELIVERY_DAYS)).strftime("%d/%m"),
    }
    return render(request, "cart.html", context)


@require_POST
def add_product_to_cart(request):
    if request.user.is_authenticated and request.user.is_staff:
        raise Http404

    product_id = request.POST.get("product_id")
    variant = request.POST.get("variant", "Mặc định")
    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    if product_id:
        product = get_object_or_404(Product, id=product_id)
        cart = get_or_create_cart(request)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={"price": product.price, "quantity": quantity},
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        messages.success(request, f"Đã thêm {product.name} vào giỏ hàng")

    return redirect(reverse("cart:cart"))


@require_POST
def delete_cart_item(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()
    messages.success(request, "Đã xóa sản phẩm khỏi giỏ hàng")
    return redirect(reverse("cart:cart"))
