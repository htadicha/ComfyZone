from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Address, Profile, User
from .utils import send_verification_email


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "first_name", "last_name", "is_staff", "is_active", "is_verified", "date_joined"]
    list_filter = ["is_staff", "is_active", "is_verified", "date_joined"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["-date_joined"]
    actions = ["mark_users_verified", "resend_verification_links"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Verification", {"fields": ("is_verified", "verification_token", "verification_token_expires")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2"),
        }),
    )

    @admin.action(description="Mark selected users as verified")
    def mark_users_verified(self, request, queryset):
        updated = queryset.update(
            is_verified=True,
            is_active=True,
            verification_token=None,
            verification_token_expires=None,
        )
        self.message_user(request, f"{updated} user(s) marked as verified.")

    @admin.action(description="Resend verification email")
    def resend_verification_links(self, request, queryset):
        sent = 0
        failed = 0

        for user in queryset:
            if user.is_verified:
                continue
            try:
                send_verification_email(user, signup=False)
            except Exception:
                failed += 1
            else:
                sent += 1

        if sent:
            self.message_user(request, f"Verification email sent to {sent} user(s).", level=messages.SUCCESS)
        if failed:
            self.message_user(
                request,
                f"Failed to send verification email to {failed} user(s). See server logs for details.",
                level=messages.ERROR,
            )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "phone_number", "created_at"]
    search_fields = ["user__email", "phone_number"]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["user", "address_type", "street_address", "city", "state", "is_default", "created_at"]
    list_filter = ["address_type", "is_default", "country"]
    search_fields = ["user__email", "street_address", "city", "state"]
