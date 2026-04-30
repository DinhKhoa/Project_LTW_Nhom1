from .services import CartService


def cart_count(request):
    """
    Context processor to provide the total number of items in the cart.
    """
    if request.user.is_authenticated and request.user.is_staff:
        return {}

    # Ensure session exists for guests
    if not request.session.session_key:
        request.session.create()

    try:
        cart = CartService.get_or_create_cart(request)
        return {"cart_count": cart.items.count()}
    except Exception as e:
        print(f"Cart context processor error: {e}")
        return {"cart_count": 0}
