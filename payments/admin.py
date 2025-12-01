from django.contrib import admin
from django.utils.html import format_html
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "transaction_id",
        "order",
        "payment_method",
        "amount",
        "status_badge",
        "created_at",
    ]
    list_filter = ["status", "payment_method", "created_at"]
    search_fields = ["transaction_id", "order__order_number", "stripe_payment_intent_id"]
    readonly_fields = ["created_at", "updated_at", "metadata"]
    fieldsets = (
        ("Payment Information", {
            "fields": ("order", "payment_method", "transaction_id", "stripe_payment_intent_id")
        }),
        ("Amount & Status", {
            "fields": ("amount", "status", "failure_reason")
        }),
        ("Metadata", {
            "fields": ("metadata",),
            "classes": ("collapse",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )

    def status_badge(self, obj):
        color_map = {
            "pending": "warning",
            "processing": "info",
            "completed": "success",
            "failed": "danger",
            "refunded": "secondary",
        }
        color = color_map.get(obj.status, "secondary")
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = "Status"
