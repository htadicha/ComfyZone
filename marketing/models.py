import uuid

from django.conf import settings
from django.core.validators import EmailValidator
from django.db import models
from django.utils import timezone


class NewsletterSubscriber(models.Model):
    """Newsletter subscriber model."""

    email = models.EmailField(unique=True, validators=[EmailValidator()])
    name = models.CharField(max_length=200, blank=True)
    source = models.CharField(max_length=100, blank=True, default="Footer CTA")
    consent = models.BooleanField(default=False)
    consent_text = models.CharField(max_length=255, blank=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    confirmation_token = models.UUIDField(default=uuid.uuid4, editable=False)
    unsubscribe_token = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        ordering = ["-subscribed_at"]
        verbose_name = "Newsletter Subscriber"
        verbose_name_plural = "Newsletter Subscribers"

    def __str__(self):
        return f"{self.email} ({self.name or 'No name'})"

    def issue_confirmation_token(self):
        """Refresh confirmation token (used for double opt-in)."""
        self.confirmation_token = uuid.uuid4()
        self.save(update_fields=["confirmation_token"])
        return self.confirmation_token

    def issue_unsubscribe_token(self):
        """Refresh unsubscribe token."""
        self.unsubscribe_token = uuid.uuid4()
        self.save(update_fields=["unsubscribe_token"])
        return self.unsubscribe_token

    def confirm(self):
        """Mark subscription as confirmed/active."""
        self.is_active = True
        self.confirmed_at = timezone.now()
        self.save(update_fields=["is_active", "confirmed_at"])

    def unsubscribe(self):
        """Unsubscribe from newsletter."""
        self.is_active = False
        self.unsubscribed_at = timezone.now()
        self.save(update_fields=["is_active", "unsubscribed_at"])


class MarketingLead(models.Model):
    """High-intent lead captured from marketing CTA."""

    STATUS_CHOICES = [
        ("new", "New"),
        ("contacted", "Contacted"),
        ("qualified", "Qualified"),
        ("won", "Won"),
        ("lost", "Lost"),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField(validators=[EmailValidator()])
    phone = models.CharField(max_length=20, blank=True)
    interest = models.CharField(max_length=120, blank=True, help_text="Product or service of interest")
    message = models.TextField(blank=True)
    consent = models.BooleanField(default=False)
    source = models.CharField(max_length=100, default="Website lead form")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="marketing_leads",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.email})"
