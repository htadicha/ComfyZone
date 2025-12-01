def cart_context(request):
    """Context processor to add cart information to all templates."""
    from cart.utils import get_cart
    cart = get_cart(request)
    cart_count = cart.get_total_items() if cart else 0
    cart_total = cart.get_total() if cart else 0
    return {
        'cart': cart,
        'cart_count': cart_count,
        'cart_total': cart_total,
    }


