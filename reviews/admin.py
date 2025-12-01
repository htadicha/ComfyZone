from django.contrib import admin
from django.utils.html import format_html
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "user",
        "rating_stars",
        "title",
        "is_approved",
        "is_verified_purchase",
        "created_at",
    ]
    list_filter = ["rating", "is_approved", "is_verified_purchase", "created_at"]
    search_fields = ["product__name", "user__email", "title", "comment"]
    readonly_fields = ["created_at", "updated_at", "is_verified_purchase"]
    fieldsets = (
        ("Review Information", {
            "fields": ("product", "user", "rating", "title", "comment")
        }),
        ("Status", {
            "fields": ("is_approved", "is_verified_purchase", "helpful_count")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )

    def rating_stars(self, obj):
        stars = "★" * obj.rating + "☆" * (5 - obj.rating)
        return format_html('<span style="color: gold;">{}</span>', stars)
    rating_stars.short_description = "Rating"

    actions = ["approve_reviews", "reject_reviews"]

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"{queryset.count()} reviews approved.")
    approve_reviews.short_description = "Approve selected reviews"

    def reject_reviews(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f"{queryset.count()} reviews rejected.")
    reject_reviews.short_description = "Reject selected reviews"
