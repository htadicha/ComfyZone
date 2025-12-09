from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Order, OrderItem
from cart.models import Cart, CartItem
from cart.utils import get_cart, get_session_cart, get_session_cart_total
from store.models import Product
from accounts.models import Address


@login_required
def order_history(request):
    """View user's order history."""
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "orders/history.html", {"orders": orders})


@login_required
def order_detail(request, order_number):
    """View order details."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, "orders/detail.html", {"order": order})


def create_order_from_cart(request, shipping_address_id=None, billing_address_id=None):
    """Create order from cart items."""
    with transaction.atomic():
        if request.user.is_authenticated:
            cart = get_cart(request)
            if not cart or not cart.items.exists():
                return None
            
            cart_items = cart.items.all()
        else:
            session_cart = get_session_cart(request)
            if not session_cart:
                return None
            
            cart_items = []
            for item_data in session_cart.values():
                try:
                    product = Product.objects.get(id=item_data["product_id"])
                    cart_items.append({
                        "product": product,
                        "quantity": item_data["quantity"],
                        "variations": item_data.get("variation_ids", []),
                    })
                except Product.DoesNotExist:
                    continue

        if request.user.is_authenticated:
            if shipping_address_id:
                shipping_address = Address.objects.get(id=shipping_address_id, user=request.user)
            else:
                shipping_address = Address.objects.filter(user=request.user, is_default=True).first()
            
            user = request.user
            email = user.email
            first_name = user.first_name
            last_name = user.last_name
            phone = user.profile.phone_number if hasattr(user, "profile") else ""
        else:
            shipping_address = None
            user = None

            email = request.POST.get("email")
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            phone = request.POST.get("phone")

        subtotal = Decimal("0")
        if request.user.is_authenticated:
            for item in cart_items:
                subtotal += Decimal(item.get_subtotal())
        else:
            subtotal = Decimal(get_session_cart_total(request))
        
        tax_rate = Decimal("0.1")
        tax = subtotal * tax_rate
        shipping_cost = Decimal("0")
        total = subtotal + tax + shipping_cost

        order = Order.objects.create(
            user=user,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            shipping_address=shipping_address,
            shipping_street=shipping_address.street_address if shipping_address else request.POST.get("shipping_street", ""),
            shipping_city=shipping_address.city if shipping_address else request.POST.get("shipping_city", ""),
            shipping_state=shipping_address.state if shipping_address else request.POST.get("shipping_state", ""),
            shipping_postal_code=shipping_address.postal_code if shipping_address else request.POST.get("shipping_postal_code", ""),
            shipping_country=shipping_address.country if shipping_address else request.POST.get("shipping_country", "United States"),
            subtotal=subtotal,
            tax=tax,
            shipping_cost=shipping_cost,
            total=total,
            notes=request.POST.get("notes", ""),
        )

        if request.user.is_authenticated:
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.get_item_price(),
                    subtotal=cart_item.get_subtotal(),
                )
        else:
            for item_data in cart_items:
                product = item_data["product"]
                quantity = item_data["quantity"]
                price = product.price

                if item_data.get("variations"):
                    from store.models import ProductVariation
                    variations = ProductVariation.objects.filter(id__in=item_data["variations"])
                    price += sum(v.price_adjustment for v in variations)
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=price,
                    subtotal=price * quantity,
                )

        if request.user.is_authenticated:
            cart.clear()
        else:
            request.session["cart"] = {}
            request.session.modified = True

        order.send_confirmation_email()

        return order
