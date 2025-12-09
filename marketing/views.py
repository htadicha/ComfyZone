import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .forms import MarketingLeadForm, NewsletterSubscriptionForm
from .models import MarketingLead, NewsletterSubscriber

logger = logging.getLogger(__name__)


@require_http_methods(["POST"])
def subscribe(request):
    """Newsletter subscription view."""
    form = NewsletterSubscriptionForm(request.POST)
    redirect_url = request.META.get("HTTP_REFERER", "/")

    if not form.is_valid():
        for error in form.errors.values():
            messages.error(request, error)
        return redirect(redirect_url)

    subscriber, created = NewsletterSubscriber.objects.get_or_create(email=form.cleaned_data["email"])
    subscriber.name = form.cleaned_data.get("name") or subscriber.name
    subscriber.consent = form.cleaned_data["consent"]
    subscriber.consent_text = form.fields["consent"].help_text
    subscriber.source = request.POST.get("source", subscriber.source or "Footer CTA")
    subscriber.is_active = False
    subscriber.confirmed_at = None
    subscriber.unsubscribed_at = None
    subscriber.issue_confirmation_token()
    subscriber.issue_unsubscribe_token()
    subscriber.save()

    _send_confirmation_email(request, subscriber)

    if created:
        messages.success(request, "Thanks! Please confirm your subscription via the email we just sent.")
    else:
        messages.info(request, "Check your inbox—we've re-sent the confirmation link.")

    return redirect(redirect_url)


@require_http_methods(["GET"])
def confirm_subscription(request, token):
    """Confirm newsletter opt-in using emailed token."""
    try:
        subscriber = NewsletterSubscriber.objects.get(confirmation_token=token)
    except NewsletterSubscriber.DoesNotExist:
        messages.error(request, "That confirmation link has expired or is invalid.")
        return redirect("/")

    subscriber.confirm()
    messages.success(request, "You're all set! Thanks for confirming your subscription.")
    return redirect("/")


def unsubscribe(request, token):
    """Unsubscribe from newsletter."""
    try:
        subscriber = NewsletterSubscriber.objects.get(unsubscribe_token=token)
        subscriber.unsubscribe()
        messages.success(request, "You have been unsubscribed from our newsletter.")
    except NewsletterSubscriber.DoesNotExist:
        messages.error(request, "Email not found in our subscription list.")

    return redirect("/")


@require_http_methods(["GET", "POST"])
def lead_create_view(request):
    """Capture high-intent showroom or consultation leads."""
    if request.method == "POST":
        form = MarketingLeadForm(request.POST)
        if form.is_valid():
            lead = form.save()
            _notify_marketing_team(lead)
            messages.success(request, "Thanks! A specialist will contact you within one business day.")
            return redirect("store:home")
    else:
        form = MarketingLeadForm()

    return render(request, "marketing/lead_form.html", {"form": form})


@login_required
@user_passes_test(lambda user: user.is_staff)
def lead_list_view(request):
    """Staff dashboard listing captured marketing leads."""
    status = request.GET.get("status", "")
    leads = MarketingLead.objects.all()
    if status:
        leads = leads.filter(status=status)

    return render(
        request,
        "marketing/lead_list.html",
        {
            "leads": leads,
            "status": status,
            "status_choices": MarketingLead.STATUS_CHOICES,
        },
    )


def _send_confirmation_email(request, subscriber: NewsletterSubscriber):
    """Send confirmation and unsubscribe links to the subscriber."""
    confirm_url = request.build_absolute_uri(
        reverse("marketing:confirm_subscription", args=[subscriber.confirmation_token])
    )
    unsubscribe_url = request.build_absolute_uri(
        reverse("marketing:unsubscribe", args=[subscriber.unsubscribe_token])
    )

    subject = "Please confirm your ComfyZone subscription"
    message = (
        "Thanks for subscribing to ComfyZone!\n\n"
        f"Please confirm your email by clicking the link below:\n{confirm_url}\n\n"
        "You can unsubscribe anytime using the link below:\n"
        f"{unsubscribe_url}"
    )
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [subscriber.email],
            fail_silently=False,
        )
    except Exception:
        logger.exception("Failed to send newsletter confirmation email to %s", subscriber.email)
        messages.error(
            request,
            "We could not send the confirmation email right now. Please try again later or contact support.",
        )


def _notify_marketing_team(lead: MarketingLead):
    """Send a lightweight notification email when a lead is captured."""
    if not settings.DEFAULT_FROM_EMAIL:
        return

    subject = f"New marketing lead: {lead.name}"
    message = (
        f"Name: {lead.name}\n"
        f"Email: {lead.email}\n"
        f"Phone: {lead.phone or 'N/A'}\n"
        f"Interest: {lead.interest or 'N/A'}\n"
        f"Message:\n{lead.message or '---'}\n"
        f"Consent: {'Yes' if lead.consent else 'No'}\n"
        f"Captured: {timezone.localtime(lead.created_at):%Y-%m-%d %H:%M}"
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [settings.DEFAULT_FROM_EMAIL],
        fail_silently=True,
    )
