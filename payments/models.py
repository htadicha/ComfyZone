from django.db import models
from django.conf import settings
from orders.models import Order


class Payment(models.Model):
    """Payment model."""
    
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("stripe", "Stripe"),
        ("paypal", "PayPal"),
        ("bank_transfer", "Bank Transfer"),
        ("cash", "Cash on Delivery"),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default="stripe")
    transaction_id = models.CharField(max_length=255, unique=True, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    failure_reason = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment {self.transaction_id} for Order {self.order.order_number}"

    def get_status_display_class(self):
        """Get Bootstrap class for status badge."""
        status_classes = {
            "pending": "warning",
            "processing": "info",
            "completed": "success",
            "failed": "danger",
            "refunded": "secondary",
        }
        return status_classes.get(self.status, "secondary")
