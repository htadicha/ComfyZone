from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from decimal import Decimal
import stripe
import json

from orders.models import Order
from orders.views import create_order_from_cart
from .models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


def checkout_view(request):
    """Checkout page view."""
    from cart.utils import get_cart, get_session_cart
    from cart.models import CartItem
    from store.models import Product

    if request.user.is_authenticated:
        cart = get_cart(request)
        if not cart or not cart.items.exists():
            messages.warning(request, "Your cart is empty.")
            return redirect("cart:view")
        items = []
        for cart_item in cart.items.all():
            items.append({
                "product": cart_item.product,
                "quantity": cart_item.quantity,
                "subtotal": cart_item.get_subtotal(),
            })
        total = cart.get_total()
    else:
        session_cart = get_session_cart(request)
        if not session_cart:
            messages.warning(request, "Your cart is empty.")
            return redirect("cart:view")
        
        items = []
        total = Decimal('0')
        for item_data in session_cart.values():
            try:
                product = Product.objects.get(id=item_data["product_id"])
                quantity = item_data["quantity"]
                price = product.price

                if item_data.get("variation_ids"):
                    from store.models import ProductVariation
                    variations = ProductVariation.objects.filter(id__in=item_data["variation_ids"])
                    price += sum(Decimal(str(v.price_adjustment)) for v in variations)

                items.append({
                    "product": product,
                    "quantity": quantity,
                    "price": price,
                    "subtotal": price * quantity,
                })
                total += price * quantity
            except Product.DoesNotExist:
                continue
    
    addresses = []
    if request.user.is_authenticated:
        try:
            from accounts.models import Address
            addresses = Address.objects.filter(user=request.user)
        except:
            pass

    subtotal = total
    tax_rate = Decimal('0.1')
    tax = subtotal * tax_rate
    shipping_cost = Decimal('0')
    final_total = subtotal + tax + shipping_cost
    
    context = {
        "items": items,
        "subtotal": subtotal,
        "tax": tax,
        "shipping_cost": shipping_cost,
        "total": final_total,
        "addresses": addresses,
        "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
    }
    
    return render(request, "payments/checkout.html", context)


@require_http_methods(["POST"])
def create_checkout_session(request):
    """Create Stripe checkout session."""
    try:
        from orders.views import create_order_from_cart
        shipping_address_id = request.POST.get("shipping_address_id")
        order = create_order_from_cart(request, shipping_address_id=shipping_address_id)

        if not order:
            return JsonResponse({"error": "Failed to create order"}, status=400)

        line_items = []
        for item in order.items.all():
            price_cents = int(float(item.price) * 100)
            line_items.append({
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": item.product_name,
                    },
                    "unit_amount": price_cents,
                },
                "quantity": item.quantity,
            })

        if order.tax > 0:
            tax_cents = int(float(order.tax) * 100)
            line_items.append({
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "Tax",
                    },
                    "unit_amount": tax_cents,
                },
                "quantity": 1,
            })
        
        if order.shipping_cost > 0:
            shipping_cents = int(float(order.shipping_cost) * 100)
            line_items.append({
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "Shipping",
                    },
                    "unit_amount": shipping_cents,
                },
                "quantity": 1,
            })

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=request.build_absolute_uri(f"/payments/success/?order={order.order_number}"),
            cancel_url=request.build_absolute_uri("/payments/cancel/"),
            customer_email=order.email,
            metadata={
                "order_number": order.order_number,
            },
        )

        Payment.objects.create(
            order=order,
            payment_method="stripe",
            transaction_id=checkout_session.id,
            stripe_payment_intent_id=checkout_session.payment_intent or "",
            amount=order.total,
            status="pending",
        )

        return JsonResponse({"sessionId": checkout_session.id})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def payment_success(request):
    """Payment success page."""
    order_number = request.GET.get("order")
    if order_number:
        try:
            order = Order.objects.get(order_number=order_number)
            payment = Payment.objects.filter(order=order).first()
            
            if payment:
                payment.status = "completed"
                payment.save()
                
                order.status = "accepted"
                order.save()
            
            return render(request, "payments/success.html", {"order": order})
        except Order.DoesNotExist:
            pass
    
    return render(request, "payments/success.html")


def payment_cancel(request):
    """Payment cancel page."""
    messages.info(request, "Payment was cancelled.")
    return render(request, "payments/cancel.html")


@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhooks."""
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        handle_checkout_session_completed(session)
    elif event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        handle_payment_intent_succeeded(payment_intent)
    elif event["type"] == "payment_intent.payment_failed":
        payment_intent = event["data"]["object"]
        handle_payment_intent_failed(payment_intent)
    
    return HttpResponse(status=200)


def handle_checkout_session_completed(session):
    """Handle successful checkout session."""
    order_number = session.get("metadata", {}).get("order_number")
    if order_number:
        try:
            order = Order.objects.get(order_number=order_number)
            payment = Payment.objects.filter(order=order).first()
            
            if payment:
                payment.status = "completed"
                payment.stripe_payment_intent_id = session.get("payment_intent", "")
                payment.save()
                
                order.status = "accepted"
                order.save()
        except Order.DoesNotExist:
            pass


def handle_payment_intent_succeeded(payment_intent):
    """Handle successful payment intent."""
    payment_intent_id = payment_intent.get("id")
    try:
        payment = Payment.objects.get(stripe_payment_intent_id=payment_intent_id)
        payment.status = "completed"
        payment.save()
        
        order = payment.order
        order.status = "accepted"
        order.save()
    except Payment.DoesNotExist:
        pass


def handle_payment_intent_failed(payment_intent):
    """Handle failed payment intent."""
    payment_intent_id = payment_intent.get("id")
    try:
        payment = Payment.objects.get(stripe_payment_intent_id=payment_intent_id)
        payment.status = "failed"
        payment.failure_reason = payment_intent.get("last_payment_error", {}).get("message", "")
        payment.save()
    except Payment.DoesNotExist:
        pass
