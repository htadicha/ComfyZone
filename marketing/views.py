from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import NewsletterSubscriber
from .forms import NewsletterSubscriptionForm


@require_http_methods(["POST"])
def subscribe(request):
    """Newsletter subscription view."""
    email = request.POST.get("email", "").strip()
    name = request.POST.get("name", "").strip()
    
    if not email:
        messages.error(request, "Please provide a valid email address.")
        return redirect(request.META.get("HTTP_REFERER", "/"))
    
    # Check for duplicate
    subscriber, created = NewsletterSubscriber.objects.get_or_create(
        email=email,
        defaults={"name": name, "is_active": True}
    )
    
    if not created:
        if subscriber.is_active:
            messages.info(request, "You are already subscribed to our newsletter!")
        else:
            # Resubscribe
            subscriber.is_active = True
            subscriber.name = name or subscriber.name
            subscriber.unsubscribed_at = None
            subscriber.save()
            messages.success(request, "Welcome back! You have been resubscribed to our newsletter.")
    else:
        messages.success(request, "Thank you for subscribing to our newsletter!")
    
    # Redirect back or to home
    return redirect(request.META.get("HTTP_REFERER", "/"))


def unsubscribe(request, email):
    """Unsubscribe from newsletter."""
    try:
        subscriber = NewsletterSubscriber.objects.get(email=email)
        subscriber.unsubscribe()
        messages.success(request, "You have been unsubscribed from our newsletter.")
    except NewsletterSubscriber.DoesNotExist:
        messages.error(request, "Email not found in our subscription list.")
    
    return redirect("/")
