from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["product", "product_name", "product_sku", "quantity", "price", "subtotal"]
    fields = ["product", "product_name", "product_sku", "quantity", "price", "subtotal"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "order_number",
        "user",
        "email",
        "status_badge",
        "total",
        "created_at",
    ]
    list_filter = ["status", "created_at"]
    search_fields = ["order_number", "email", "user__email", "first_name", "last_name"]
    readonly_fields = ["order_number", "created_at", "updated_at"]
    inlines = [OrderItemInline]
    fieldsets = (
        ("Order Information", {
            "fields": ("order_number", "user", "email", "status", "created_at", "updated_at")
        }),
        ("Customer Information", {
            "fields": ("first_name", "last_name", "phone")
        }),
        ("Shipping Address", {
            "fields": (
                "shipping_address",
                "shipping_street",
                "shipping_city",
                "shipping_state",
                "shipping_postal_code",
                "shipping_country",
            )
        }),
        ("Billing Address", {
            "fields": (
                "billing_street",
                "billing_city",
                "billing_state",
                "billing_postal_code",
                "billing_country",
            ),
            "classes": ("collapse",)
        }),
        ("Order Totals", {
            "fields": ("subtotal", "tax", "shipping_cost", "total")
        }),
        ("Notes", {
            "fields": ("notes",)
        }),
    )

    def status_badge(self, obj):
        """Render a colored status badge for admin list display."""
        color_map = {
            "new": "primary",
            "accepted": "info",
            "completed": "success",
            "cancelled": "danger",
        }
        color = color_map.get(obj.status, "secondary")
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = "Status"

    def save_model(self, request, obj, form, change):
        """Save the order and trigger confirmation when status changes."""
        super().save_model(request, obj, form, change)
        if change and "status" in form.changed_data:
            if obj.status == "accepted":
                obj.send_confirmation_email()


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "product_name", "quantity", "price", "subtotal", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["order__order_number", "product_name", "product_sku"]
