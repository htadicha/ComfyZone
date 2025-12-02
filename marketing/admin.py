from django.contrib import admin
from django.http import HttpResponse
import csv
from .models import MarketingLead, NewsletterSubscriber


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ["email", "name", "is_active", "subscribed_at", "unsubscribed_at"]
    list_filter = ["is_active", "subscribed_at"]
    search_fields = ["email", "name"]
    readonly_fields = ["subscribed_at", "unsubscribed_at"]
    actions = ["export_csv", "export_latest"]

    def export_csv(self, request, queryset):
        """Export selected subscribers to CSV."""
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="newsletter_subscribers.csv"'

        writer = csv.writer(response)
        writer.writerow(["Email", "Name", "Subscribed At", "Is Active"])

        for subscriber in queryset:
            writer.writerow([
                subscriber.email,
                subscriber.name,
                subscriber.subscribed_at.strftime("%Y-%m-%d %H:%M:%S"),
                subscriber.is_active,
            ])

        return response
    export_csv.short_description = "Export selected to CSV"

    def export_latest(self, request, queryset):
        """Export latest subscribers (last 30 days) to CSV."""
        from django.utils import timezone
        from datetime import timedelta

        thirty_days_ago = timezone.now() - timedelta(days=30)
        latest_subscribers = NewsletterSubscriber.objects.filter(
            subscribed_at__gte=thirty_days_ago,
            is_active=True
        )

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="latest_subscribers.csv"'

        writer = csv.writer(response)
        writer.writerow(["Email", "Name", "Subscribed At"])

        for subscriber in latest_subscribers:
            writer.writerow([
                subscriber.email,
                subscriber.name,
                subscriber.subscribed_at.strftime("%Y-%m-%d %H:%M:%S"),
            ])

        return response
    export_latest.short_description = "Export latest subscribers (last 30 days)"


@admin.register(MarketingLead)
class MarketingLeadAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone", "interest", "status", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["name", "email", "interest"]
    autocomplete_fields = ["assigned_to"]
