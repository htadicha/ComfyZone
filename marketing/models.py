from django.db import models
from django.core.validators import EmailValidator
from django.utils import timezone


class NewsletterSubscriber(models.Model):
    """Newsletter subscriber model."""
    
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    name = models.CharField(max_length=200, blank=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-subscribed_at"]
        verbose_name = "Newsletter Subscriber"
        verbose_name_plural = "Newsletter Subscribers"

    def __str__(self):
        return f"{self.email} ({self.name or 'No name'})"

    def unsubscribe(self):
        """Unsubscribe from newsletter."""
        self.is_active = False
        self.unsubscribed_at = timezone.now()
        self.save()
