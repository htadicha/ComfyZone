from urllib.parse import urlsplit, urlunsplit

from django.conf import settings


def cart_context(request):
    """Context processor to add cart information to all templates."""
    from cart.utils import get_cart
    cart = get_cart(request)
    cart_count = cart.get_total_items() if cart else 0
    cart_total = cart.get_total() if cart else 0
    return {
        "cart": cart,
        "cart_count": cart_count,
        "cart_total": cart_total,
    }


def site_context(request):
    """Expose canonical URL and site metadata to templates."""
    absolute_url = request.build_absolute_uri()
    split = urlsplit(absolute_url)
    canonical = urlunsplit((split.scheme, split.netloc, split.path, "", ""))

    return {
        "site_name": "ComfyZone",
        "site_url": settings.SITE_URL.rstrip("/"),
        "canonical_url": canonical,
    }

