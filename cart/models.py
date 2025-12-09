from django.db import models
from django.conf import settings
from store.models import Product, ProductVariation


class Cart(models.Model):
    """Cart model for authenticated users."""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return a label for the cart owner."""
        return f"Cart for {self.user.email}"

    def get_total(self):
        """Calculate total cart value."""
        return sum(item.get_subtotal() for item in self.items.all())

    def get_total_items(self):
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items.all())

    def clear(self):
        """Clear all items from cart."""
        self.items.all().delete()


class CartItem(models.Model):
    """Cart item model."""
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    variations = models.ManyToManyField(ProductVariation, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["cart", "product"]

    def __str__(self):
        """Return a label combining quantity and product."""
        return f"{self.quantity}x {self.product.name}"

    def get_subtotal(self):
        """Calculate subtotal for this item including variations."""
        base_price = self.product.price

        variation_adjustment = sum(
            variation.price_adjustment for variation in self.variations.all()
        )

        item_price = base_price + variation_adjustment
        return item_price * self.quantity

    def get_item_price(self):
        """Get single item price including variations."""
        base_price = self.product.price
        variation_adjustment = sum(
            variation.price_adjustment for variation in self.variations.all()
        )
        return base_price + variation_adjustment
