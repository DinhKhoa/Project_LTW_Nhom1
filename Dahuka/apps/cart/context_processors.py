from .services import CartService

def cart_count(request):
    if request.user.is_authenticated and request.user.is_staff:
        return {}

    if not request.session.session_key:
        request.session.create()

    try:
        cart = CartService.get_or_create_cart(request)
        return {"cart_count": cart.items.count()}
    except Exception:
        return {"cart_count": 0}
