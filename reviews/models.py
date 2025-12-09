from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from store.models import Product


class Review(models.Model):
    """Product review model."""

    RATING_CHOICES = [
        (1, "1 Star"),
        (2, "2 Stars"),
        (3, "3 Stars"),
        (4, "4 Stars"),
        (5, "5 Stars"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    is_verified_purchase = models.BooleanField(default=False)
    helpful_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["product", "user"]
        ordering = ["-created_at"]

    def __str__(self):
        """Return the reviewer, product, and rating summary."""
        return f"{self.user.email} - {self.product.name} - {self.rating} stars"

    def save(self, *args, **kwargs):
        """Persist review, marking verified purchases and refreshing product data."""
        if not self.pk:
            from orders.models import OrderItem
            has_purchased = OrderItem.objects.filter(
                order__user=self.user,
                product=self.product
            ).exists()
            self.is_verified_purchase = has_purchased

        super().save(*args, **kwargs)

        self.product.save()
