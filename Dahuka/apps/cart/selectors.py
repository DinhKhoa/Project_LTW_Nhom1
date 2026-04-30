from typing import List, Optional, Any
from django.db.models import QuerySet
from .models import Cart, CartItem

def get_cart_items(cart: Cart, selected_ids: Optional[List[int]] = None) -> QuerySet[CartItem]:
    """
    Retrieves items for a given cart, optionally filtering by selected IDs.
    """
    items = cart.items.all().select_related("product")
    if selected_ids is not None:
        items = items.filter(id__in=selected_ids)
    return items

def get_cart_by_user_or_session(user: Any, session_key: Optional[str]) -> Optional[Cart]:
    """
    Retrieves a cart based on user authentication or session key.
    """
    if user.is_authenticated:
        return Cart.objects.filter(user=user).first()
    if session_key:
        return Cart.objects.filter(session_key=session_key).first()
    return None
