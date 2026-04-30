from typing import Any, Dict, List, Optional
from django.db import transaction
from django.contrib.auth.models import User
from decimal import Decimal
from apps.promotions.models import Promotion
from apps.orders.services import OrderService
from .models import Cart, CartItem


class CartService:
    """Service class for shopping cart operations."""

    @staticmethod
    def get_or_create_cart(request) -> Cart:
        """
        Retrieves existing cart from session/user or creates a new one.
        Handles merging session cart into user cart upon login.
        """
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        if request.user.is_authenticated:
            user_cart, created = Cart.objects.get_or_create(user=request.user)
            # Merge session cart if it exists
            session_cart = Cart.objects.filter(session_key=session_key).first()
            if session_cart and session_cart != user_cart:
                for item in session_cart.items.all():
                    # Update or create items in user cart
                    existing_item = user_cart.items.filter(
                        product=item.product, 
                        variant=item.variant
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
    def add_to_cart(cart: Cart, product: Any, quantity: int, variant: str) -> CartItem:
        """
        Adds a product variant to the cart or updates quantity if already exists.
        Captures current product price.
        """
        item, created = CartItem.objects.get_or_create(
            cart=cart, 
            product=product, 
            variant=variant,
            defaults={
                'quantity': quantity,
                'price': product.price
            }
        )
        if not created:
            item.quantity += quantity
            item.price = product.price # Update to latest price
            item.save()
        return item

    @staticmethod
    def get_applied_promotions(total_price: float) -> List[Dict[str, Any]]:
        """
        Finds all currently valid promotions that meet the condition.
        Returns a list of dicts with promotion info and calculated discount.
        Priority: Fixed amount discounts first, then percentage discounts.
        """
        from django.utils import timezone
        today = timezone.localtime().date()
        
        # Get all valid and active promotions
        promos = Promotion.objects.filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today,
            condition__lte=total_price
        )
        
        applied = []
        current_total = float(total_price)
        
        # Separate and sort: fixed first, then percent
        fixed_promos = promos.filter(discount_type='fixed').order_by('-value')
        percent_promos = promos.filter(discount_type='percent').order_by('-value')
        
        # 1. Apply Fixed discounts
        for promo in fixed_promos:
            if current_total <= 0: break
            discount = min(float(promo.value), current_total)
            if discount > 0:
                applied.append({
                    "name": promo.name,
                    "code": promo.code,
                    "discount_amount": discount,
                    "formatted_discount": f"-{Decimal(str(discount)):.0f}" # Temporary, will format in template
                })
                current_total -= discount
                
        # 2. Apply Percentage discounts (on the original total_price for maximum benefit, 
        # or on current_total? Let's use original total as per common practice, but capped by current_total)
        for promo in percent_promos:
            if current_total <= 0: break
            discount = (float(promo.value) / 100) * float(total_price)
            discount = min(discount, current_total)
            if discount > 0:
                applied.append({
                    "name": promo.name,
                    "code": promo.code,
                    "discount_amount": discount,
                    "formatted_discount": f"-{Decimal(str(discount)):.0f}"
                })
                current_total -= discount
                
        return applied
    @staticmethod
    @transaction.atomic
    def create_order_from_cart(
        user: Optional[User],
        cart_obj: Cart,
        customer_data: Dict[str, Any],
        order_items_data: List[Dict[str, Any]],
        payment_type: str = 'full',
        deposit_amount: float = 0,
        note: str = ""
    ) -> Any:
        """
        Orchestrates order creation using OrderService.
        Automatically applies all eligible promotions.
        """
        total_price = sum(float(item['price']) * int(item['quantity']) for item in order_items_data)
        
        # Recalculate auto-promotions for the order
        applied_promos = CartService.get_applied_promotions(total_price)
        discount_amount = sum(p['discount_amount'] for p in applied_promos)
        
        payment_status = 'da_thanh_toan' if payment_type == 'full' else 'chua_thanh_toan'

        if payment_type == 'full':
            deposit_amount = total_price - discount_amount

        order = OrderService.create_order(
            customer=user,
            full_name=customer_data.get("full_name", ""),
            phone=customer_data.get("phone", ""),
            city=customer_data.get("province", ""),
            district=customer_data.get("district", ""),
            ward=customer_data.get("ward", ""),
            house_details=customer_data.get("address_detail", ""),
            cart_items=order_items_data,
            discount_amount=discount_amount,
            deposit_amount=deposit_amount,
            payment_method=payment_type,
            payment_status=payment_status,
            note=note
        )
        return order

    @staticmethod
    def get_cart_totals(cart: Cart, state: Dict[str, Any], apply_promos: bool = True) -> Dict[str, Any]:
        """
        Calculates all cart totals based on current state.
        apply_promos: If True, automatically applies all eligible promotions.
        """
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
        remaining_amount = final_total - deposit_amount

        return {
            "total_price": total_price,
            "shipping_fee": shipping_fee,
            "discount_amount": discount_amount,
            "applied_promotions": applied_promotions,
            "final_total": final_total,
            "deposit_amount": deposit_amount,
            "remaining_amount": remaining_amount,
            "deposit_percent": deposit_percent,
        }

    @staticmethod
    @transaction.atomic
    def reorder(cart: Cart, order: Any) -> List[int]:
        """
        Adds all items from a previous order to the cart.
        Returns the list of CartItem IDs that were added or updated.
        """
        item_ids = []
        # Import OrderItem inside to avoid circular dependency if any
        from apps.orders.models import OrderItem
        
        for order_item in order.items.all():
            if order_item.product:
                # We default variant to "Mặc định" as OrderItem doesn't store variants
                cart_item = CartService.add_to_cart(
                    cart=cart,
                    product=order_item.product,
                    quantity=order_item.quantity,
                    variant="Mặc định"
                )
                item_ids.append(cart_item.id)
        return item_ids
