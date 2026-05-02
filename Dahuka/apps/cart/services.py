from typing import Any, Dict, List, Optional
from django.db import transaction
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.urls import reverse
from django.shortcuts import get_object_or_404
from decimal import Decimal
from apps.promotions.models import Promotion
from apps.orders.services import OrderService
from apps.products.models import Product
from apps.core.utils import format_money
from .models import Cart, CartItem
from apps.core.constants import CART_DEFAULT_DEPOSIT_PERCENT

class CartService:

    @staticmethod
    def get_or_create_cart(request: HttpRequest) -> Cart:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        if request.user.is_authenticated:
            user_cart, created = Cart.objects.get_or_create(user=request.user)
            session_cart = Cart.objects.filter(session_key=session_key).first()
            if session_cart and session_cart != user_cart:
                for item in session_cart.items.all():
                    existing_item = user_cart.items.filter(
                        product=item.product
                    ).first()
                    if existing_item:
                        existing_item.quantity += item.quantity
                        existing_item.save()
                    else:
                        item.cart = user_cart
                        item.save()
                session_cart.delete()
            return user_cart
        
        cart, created = Cart.objects.get_or_create(session_key=session_key)
        return cart

    @staticmethod
    def get_checkout_state(request: HttpRequest) -> Dict[str, Any]:
        if "checkout_state" not in request.session:
            customer_data = {
                "full_name": "", "phone": "", "province": "", "district": "",
                "ward": "", "address_detail": "", "address_type": "home",
                "is_default": False, "id": None,
            }

            if request.user.is_authenticated:
                try:
                    profile = request.user.customer
                    customer_data["full_name"] = request.user.get_full_name() or request.user.username
                    customer_data["phone"] = profile.phone
                    default_addr = profile.addresses.filter(is_default=True).first() or profile.addresses.first()
                    if default_addr:
                        customer_data.update({
                            "full_name": default_addr.full_name, "phone": default_addr.phone,
                            "province": default_addr.province, "district": default_addr.district,
                            "ward": default_addr.ward, "address_detail": default_addr.address_detail,
                            "address_type": default_addr.address_type, "is_default": default_addr.is_default,
                            "id": default_addr.id,
                        })
                except: pass

            request.session["checkout_state"] = {
                "current_screen": "cart",
                "cart_payment_type": "full",
                "deposit_percent": CART_DEFAULT_DEPOSIT_PERCENT,
                "coupon_code": "",
                "customer": customer_data,
                "selected_ids": [],
            }

        state = request.session["checkout_state"]
        if request.user.is_authenticated and not state["customer"].get("full_name"):
            try:
                profile = request.user.customer
                default_addr = profile.addresses.filter(is_default=True).first() or profile.addresses.first()
                if default_addr:
                    state["customer"].update({
                        "full_name": default_addr.full_name, "phone": default_addr.phone,
                        "province": default_addr.province, "district": default_addr.district,
                        "ward": default_addr.ward, "address_detail": default_addr.address_detail,
                        "address_type": default_addr.address_type, "id": default_addr.id,
                    })
                    request.session.modified = True
            except: pass
        
        if "selected_ids" not in state: state["selected_ids"] = []
        return state

    @staticmethod
    def handle_cart_action(request: HttpRequest, cart_obj: Cart, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        action = request.POST.get("action")
        if not action: return None

        if action == "toggle_select":
            item_id = int(request.POST.get("item_id"))
            is_selected = request.POST.get("is_selected") == "true"
            if is_selected:
                if item_id not in state["selected_ids"]: state["selected_ids"].append(item_id)
            else:
                if item_id in state["selected_ids"]: state["selected_ids"].remove(item_id)
        
        elif action == "toggle_select_all":
            is_selected = request.POST.get("is_selected") == "true"
            state["selected_ids"] = [item.id for item in cart_obj.items.all()] if is_selected else []

        elif action == "bulk_delete":
            selected_ids = state.get("selected_ids", [])
            if selected_ids:
                cart_obj.items.filter(id__in=selected_ids).delete()
                state["selected_ids"] = []

        elif action == "update_quantity":
            item_id = request.POST.get("item_id")
            quantity = int(request.POST.get("quantity", 1))
            if quantity >= 1:
                CartItem.objects.filter(id=item_id, cart=cart_obj).update(quantity=quantity)

        elif action == "update_payment_type":
            state["cart_payment_type"] = request.POST.get("cart_payment_type")
            if state["cart_payment_type"] == "full": state["order_method"] = "bank"

        elif action == "update_deposit":
            state["deposit_percent"] = int(request.POST.get("deposit_percent_input", 10))

        request.session.modified = True
        return state

    @staticmethod
    def get_cart_totals(cart: Cart, state: Dict[str, Any], apply_promos: bool = True) -> Dict[str, Any]:
        selected_ids = state.get("selected_ids", [])
        selected_items = cart.items.filter(id__in=selected_ids)
        total_price = sum((item.subtotal for item in selected_items), Decimal(0))
        
        applied_promotions = []
        discount_amount = 0
        if apply_promos:
            applied_promotions = CartService.get_applied_promotions(float(total_price))
            discount_amount = sum(p['discount_amount'] for p in applied_promotions)
        
        shipping_fee = 0
        final_total = max(0, float(total_price) + shipping_fee - discount_amount)
        deposit_percent = state.get("deposit_percent", 10) if selected_ids else 0
        deposit_amount = round(final_total * deposit_percent / 100)
        
        return {
            "total_price": total_price, "shipping_fee": shipping_fee,
            "discount_amount": discount_amount, "applied_promotions": applied_promotions,
            "final_total": final_total, "deposit_amount": deposit_amount,
            "remaining_amount": final_total - deposit_amount, "deposit_percent": deposit_percent,
        }

    @staticmethod
    def get_ajax_payload(cart_obj: Cart, state: Dict[str, Any]) -> Dict[str, Any]:
        apply_promos = state.get("current_screen") != "cart"
        totals = CartService.get_cart_totals(cart_obj, state, apply_promos=apply_promos)
        return {
            "cart_payment_type": state["cart_payment_type"],
            "deposit_percent": state["deposit_percent"],
            "formatted_deposit_amount": format_money(totals["deposit_amount"]),
            "formatted_total_price": format_money(totals["final_total"]),
            "formatted_base_total": format_money(totals["total_price"]),
            "discount_amount": format_money(totals["discount_amount"]),
            "coupon_code": state.get("coupon_code", ""),
            "cart_count": cart_obj.items.count(),
            "selected_count": len(state["selected_ids"]),
        }

    @staticmethod
    def add_to_cart(cart: Cart, product: Product, quantity: int) -> CartItem:
        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product,
            defaults={'quantity': quantity, 'price': product.price}
        )
        if not created:
            item.quantity += quantity
            item.price = product.price
            item.save()
        return item

    @staticmethod
    def apply_promotion(code: str, total_price: float) -> float:
        from django.utils import timezone
        today = timezone.localtime().date()
        promo = Promotion.objects.filter(code=code, is_active=True, start_date__lte=today, end_date__gte=today, condition__lte=total_price).first()
        if not promo: return 0
        return float(promo.value) if promo.discount_type == 'fixed' else (float(promo.value) / 100 * total_price)

    @staticmethod
    def get_applied_promotions(total_price: float) -> List[Dict[str, Any]]:
        from django.utils import timezone
        today = timezone.localtime().date()
        promos = Promotion.objects.filter(is_active=True, start_date__lte=today, end_date__gte=today, condition__lte=total_price)
        applied = []
        current_total = float(total_price)
        for promo in promos.filter(discount_type='fixed').order_by('-value'):
            if current_total <= 0: break
            discount = min(float(promo.value), current_total)
            applied.append({"name": promo.name, "code": promo.code, "discount_amount": discount})
            current_total -= discount
        for promo in promos.filter(discount_type='percent').order_by('-value'):
            if current_total <= 0: break
            discount = min((float(promo.value) / 100) * float(total_price), current_total)
            applied.append({"name": promo.name, "code": promo.code, "discount_amount": discount})
            current_total -= discount
        return applied

    @staticmethod
    @transaction.atomic
    def create_order_from_cart(user: Optional[User], cart_obj: Cart, customer_data: Dict[str, Any], order_items_data: List[Dict[str, Any]], payment_type: str = 'full', deposit_amount: float = 0, note: str = "") -> Any:
        total_price = sum(float(item['price']) * int(item['quantity']) for item in order_items_data)
        applied_promos = CartService.get_applied_promotions(total_price)
        discount_amount = sum(p['discount_amount'] for p in applied_promos)
        payment_status = 'da_thanh_toan' if payment_type == 'full' else 'chua_thanh_toan'
        if payment_type == 'full': deposit_amount = total_price - discount_amount

        return OrderService.create_order(
            customer=user, full_name=customer_data.get("full_name", ""), phone=customer_data.get("phone", ""),
            city=customer_data.get("province", ""), district=customer_data.get("district", ""),
            ward=customer_data.get("ward", ""), house_details=customer_data.get("address_detail", ""),
            cart_items=order_items_data, discount_amount=discount_amount, deposit_amount=deposit_amount,
            payment_method=payment_type, payment_status=payment_status, note=note
        )

    @staticmethod
    @transaction.atomic
    def reorder(cart: Cart, order: Any) -> List[int]:
        item_ids = []
        for order_item in order.items.all():
            if order_item.product:
                cart_item = CartService.add_to_cart(cart=cart, product=order_item.product, quantity=order_item.quantity)
                item_ids.append(cart_item.id)
        return item_ids
