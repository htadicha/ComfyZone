from django.contrib.sessions.models import Session
from .models import Cart, CartItem
from store.models import Product, ProductVariation


def get_cart(request):
    """Get or create cart for user or session."""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return cart
    else:
        # For guest users, return None (we'll handle session cart in views)
        return None


def get_session_cart(request):
    """Get cart data from session for guest users."""
    return request.session.get("cart", {})


def add_to_session_cart(request, product_id, quantity=1, variation_ids=None):
    """Add item to session cart."""
    cart = request.session.get("cart", {})
    item_key = str(product_id)
    
    if variation_ids:
        item_key += f"_{'-'.join(map(str, variation_ids))}"
    
    if item_key in cart:
        cart[item_key]["quantity"] += quantity
    else:
        cart[item_key] = {
            "product_id": product_id,
            "quantity": quantity,
            "variation_ids": variation_ids or [],
        }
    
    request.session["cart"] = cart
    request.session.modified = True


def update_session_cart_item(request, product_id, quantity, variation_ids=None):
    """Update item quantity in session cart."""
    cart = request.session.get("cart", {})
    item_key = str(product_id)
    
    if variation_ids:
        item_key += f"_{'-'.join(map(str, variation_ids))}"
    
    if item_key in cart:
        if quantity > 0:
            cart[item_key]["quantity"] = quantity
        else:
            del cart[item_key]
        request.session["cart"] = cart
        request.session.modified = True


def remove_from_session_cart(request, product_id, variation_ids=None):
    """Remove item from session cart."""
    cart = request.session.get("cart", {})
    item_key = str(product_id)
    
    if variation_ids:
        item_key += f"_{'-'.join(map(str, variation_ids))}"
    
    if item_key in cart:
        del cart[item_key]
        request.session["cart"] = cart
        request.session.modified = True


def get_session_cart_total(request):
    """Calculate total for session cart."""
    cart = get_session_cart(request)
    total = 0
    
    for item_data in cart.values():
        try:
            product = Product.objects.get(id=item_data["product_id"])
            quantity = item_data["quantity"]
            price = product.price
            
            # Add variation adjustments
            if item_data.get("variation_ids"):
                variations = ProductVariation.objects.filter(
                    id__in=item_data["variation_ids"]
                )
                price += sum(v.price_adjustment for v in variations)
            
            total += price * quantity
        except Product.DoesNotExist:
            continue
    
    return total


def get_session_cart_count(request):
    """Get total item count for session cart."""
    cart = get_session_cart(request)
    return sum(item["quantity"] for item in cart.values())


def merge_carts(request, user):
    """Merge session cart into user cart on login."""
    session_cart = get_session_cart(request)
    
    if not session_cart:
        return
    
    cart, created = Cart.objects.get_or_create(user=user)
    
    for item_data in session_cart.values():
        try:
            product = Product.objects.get(id=item_data["product_id"])
            quantity = item_data["quantity"]
            variation_ids = item_data.get("variation_ids", [])
            
            # Check if item with same product and variations exists
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
            )
            
            if not created:
                # Update quantity if item exists
                cart_item.quantity += quantity
            else:
                cart_item.quantity = quantity
            
            cart_item.save()
            
            # Add variations
            if variation_ids:
                variations = ProductVariation.objects.filter(id__in=variation_ids)
                cart_item.variations.set(variations)
        
        except Product.DoesNotExist:
            continue
    
    # Clear session cart after merging
    request.session["cart"] = {}
    request.session.modified = True


