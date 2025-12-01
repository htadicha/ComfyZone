from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from store.models import Product, ProductVariation
from .models import Cart, CartItem
from .utils import (
    get_cart,
    get_session_cart,
    add_to_session_cart,
    update_session_cart_item,
    remove_from_session_cart,
    get_session_cart_total,
    get_session_cart_count,
)


@require_http_methods(["POST"])
def add_to_cart(request, product_id):
    """Add product to cart."""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get("quantity", 1))
    variation_ids = request.POST.getlist("variations")
    
    if variation_ids:
        variation_ids = [int(vid) for vid in variation_ids]
        variations = ProductVariation.objects.filter(id__in=variation_ids, is_active=True)
        if variations.count() != len(variation_ids):
            messages.error(request, "Invalid product variation selected.")
            return redirect("store:product_detail", slug=product.slug)
    else:
        variations = []
    
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
        )
        
        if not item_created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        
        cart_item.save()
        
        if variations:
            cart_item.variations.set(variations)
        
        messages.success(request, f"{product.name} added to cart!")
    else:
        add_to_session_cart(request, product_id, quantity, variation_ids)
        messages.success(request, f"{product.name} added to cart!")
    
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "message": f"{product.name} added to cart!",
            "cart_count": get_session_cart_count(request) if not request.user.is_authenticated else cart.get_total_items(),
        })
    
    return redirect("cart:view")


@require_http_methods(["POST"])
def update_cart_item(request, item_id):
    """Update cart item quantity."""
    quantity = int(request.POST.get("quantity", 1))
    
    if request.user.is_authenticated:
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, "Cart updated!")
        else:
            cart_item.delete()
            messages.success(request, "Item removed from cart!")
    else:
        # Handle session cart update
        product_id = request.POST.get("product_id")
        variation_ids = request.POST.getlist("variations")
        if variation_ids:
            variation_ids = [int(vid) for vid in variation_ids]
        else:
            variation_ids = None
        
        update_session_cart_item(request, product_id, quantity, variation_ids)
        messages.success(request, "Cart updated!")
    
    return redirect("cart:view")


@require_http_methods(["POST"])
def remove_from_cart(request, item_id):
    """Remove item from cart."""
    if request.user.is_authenticated:
        if item_id > 0:
            cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
            cart_item.delete()
            messages.success(request, "Item removed from cart!")
        else:
            messages.error(request, "Invalid item.")
    else:
        product_id = request.POST.get("product_id")
        if product_id:
            # For session cart, we need the item_key
            item_key = request.POST.get("item_key")
            if item_key:
                session_cart = get_session_cart(request)
                if item_key in session_cart:
                    del session_cart[item_key]
                    request.session["cart"] = session_cart
                    request.session.modified = True
                    messages.success(request, "Item removed from cart!")
            else:
                variation_ids = request.POST.getlist("variations")
                if variation_ids:
                    variation_ids = [int(vid) for vid in variation_ids]
                else:
                    variation_ids = None
                remove_from_session_cart(request, product_id, variation_ids)
                messages.success(request, "Item removed from cart!")
        else:
            messages.error(request, "Invalid item.")
    
    return redirect("cart:view")


def view_cart(request):
    """View cart page."""
    if request.user.is_authenticated:
        cart = get_cart(request)
        if cart:
            items = []
            for cart_item in cart.items.all():
                items.append({
                    "id": cart_item.id,
                    "product": cart_item.product,
                    "quantity": cart_item.quantity,
                    "variations": cart_item.variations.all(),
                    "subtotal": cart_item.get_subtotal(),
                    "item_price": cart_item.get_item_price(),
                })
            total = cart.get_total()
            cart_count = cart.get_total_items()
        else:
            items = []
            total = 0
            cart_count = 0
    else:
        session_cart = get_session_cart(request)
        items = []
        
        for item_key, item_data in session_cart.items():
            try:
                product = Product.objects.get(id=item_data["product_id"])
                quantity = item_data["quantity"]
                variation_ids = item_data.get("variation_ids", [])
                
                variations = ProductVariation.objects.filter(id__in=variation_ids) if variation_ids else []
                
                # Calculate price with variations
                price = product.price
                if variations:
                    price += sum(v.price_adjustment for v in variations)
                
                items.append({
                    "id": 0,
                    "product": product,
                    "quantity": quantity,
                    "variations": variations,
                    "subtotal": price * quantity,
                    "item_price": price,
                    "item_key": item_key,
                })
            except Product.DoesNotExist:
                continue
        
        total = get_session_cart_total(request)
        cart_count = get_session_cart_count(request)
        cart = None
    
    context = {
        "cart": cart,
        "items": items,
        "total": total,
        "cart_count": cart_count,
    }
    
    return render(request, "cart/view.html", context)
