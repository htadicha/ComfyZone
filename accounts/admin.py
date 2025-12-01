from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, Address


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "first_name", "last_name", "is_staff", "is_active", "is_verified", "date_joined"]
    list_filter = ["is_staff", "is_active", "is_verified", "date_joined"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["-date_joined"]

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


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "phone_number", "created_at"]
    search_fields = ["user__email", "phone_number"]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["user", "address_type", "street_address", "city", "state", "is_default", "created_at"]
    list_filter = ["address_type", "is_default", "country"]
    search_fields = ["user__email", "street_address", "city", "state"]
