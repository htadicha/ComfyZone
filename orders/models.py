from django.db import models
from django.conf import settings
from django.core.mail import send_mail
from store.models import Product
from accounts.models import Address
import uuid


class Order(models.Model):
    """Order model."""
    
    STATUS_CHOICES = [
        ("new", "New"),
        ("accepted", "Accepted"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    order_number = models.CharField(max_length=50, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders"
    )
    email = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)

    shipping_address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shipping_orders"
    )

    shipping_street = models.CharField(max_length=255)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100, default="United States")

    billing_street = models.CharField(max_length=255, blank=True)
    billing_city = models.CharField(max_length=100, blank=True)
    billing_state = models.CharField(max_length=100, blank=True)
    billing_postal_code = models.CharField(max_length=20, blank=True)
    billing_country = models.CharField(max_length=100, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        """Return a short label for the order."""
        return f"Order {self.order_number}"

    def save(self, *args, **kwargs):
        """Ensure order number is set before saving."""
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    def generate_order_number(self):
        """Generate unique order number."""
        return f"ORD-{uuid.uuid4().hex[:12].upper()}"

    def get_status_display_class(self):
        """Get Bootstrap class for status badge."""
        status_classes = {
            "new": "primary",
            "accepted": "info",
            "completed": "success",
            "cancelled": "danger",
        }
        return status_classes.get(self.status, "secondary")

    def send_confirmation_email(self):
        """Send order confirmation email."""
        subject = f"Order Confirmation - {self.order_number}"
        message = f"""
        Thank you for your order!
        
        Order Number: {self.order_number}
        Total: ${self.total}
        
        We'll send you another email when your order ships.
        
        Order Details:
        {self.get_order_summary()}
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            fail_silently=False,
        )

    def get_order_summary(self):
        """Get order summary text."""
        items_text = "\n".join([
            f"- {item.product.name} x{item.quantity} - ${item.price} each"
            for item in self.items.all()
        ])
        return f"""
        Items:
        {items_text}
        
        Subtotal: ${self.subtotal}
        Tax: ${self.tax}
        Shipping: ${self.shipping_cost}
        Total: ${self.total}
        """


class OrderItem(models.Model):
    """Order item model."""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=100, blank=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        """Return a readable representation of the order item."""
        return f"{self.product_name} x{self.quantity}"

    def save(self, *args, **kwargs):
        """Snapshot product data and subtotal before saving."""
        if self.product:
            self.product_name = self.product.name
            self.product_sku = self.product.sku
        self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)
