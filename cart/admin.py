from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ["product", "quantity", "get_subtotal"]
    fields = ["product", "quantity", "variations", "get_subtotal"]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["user", "get_total_items", "get_total", "created_at", "updated_at"]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["user__email"]
    inlines = [CartItemInline]
    readonly_fields = ["created_at", "updated_at"]

    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = "Items"

    def get_total(self, obj):
        return f"${obj.get_total():.2f}"
    get_total.short_description = "Total"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ["cart", "product", "quantity", "get_subtotal", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["cart__user__email", "product__name"]

    def get_subtotal(self, obj):
        return f"${obj.get_subtotal():.2f}"
    get_subtotal.short_description = "Subtotal"
