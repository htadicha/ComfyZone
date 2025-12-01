from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, ProductVariation


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ["image", "alt_text", "is_primary", "order"]


class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 1
    fields = ["variation_type", "name", "value", "price_adjustment", "stock", "sku", "is_active"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "parent", "is_active", "created_at"]
    list_filter = ["is_active", "parent"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "category",
        "price",
        "stock",
        "is_active",
        "is_featured",
        "created_at",
        "image_preview",
    ]
    list_filter = ["is_active", "is_featured", "category", "created_at"]
    search_fields = ["name", "description", "sku"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline, ProductVariationInline]
    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "slug", "category", "description", "short_description")
        }),
        ("Pricing & Inventory", {
            "fields": ("price", "compare_at_price", "stock", "sku")
        }),
        ("Status", {
            "fields": ("is_active", "is_featured")
        }),
        ("SEO", {
            "fields": ("meta_title", "meta_description", "meta_keywords"),
            "classes": ("collapse",)
        }),
    )

    def image_preview(self, obj):
        primary_image = obj.get_primary_image()
        if primary_image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                primary_image.image.url
            )
        return "No image"
    image_preview.short_description = "Image"


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ["product", "image_preview", "is_primary", "order", "created_at"]
    list_filter = ["is_primary", "created_at"]
    search_fields = ["product__name", "alt_text"]

    def image_preview(self, obj):
        return format_html(
            '<img src="{}" width="100" height="100" style="object-fit: cover;" />',
            obj.image.url
        )
    image_preview.short_description = "Preview"


@admin.register(ProductVariation)
class ProductVariationAdmin(admin.ModelAdmin):
    list_display = ["product", "variation_type", "name", "price_adjustment", "stock", "is_active"]
    list_filter = ["variation_type", "is_active"]
    search_fields = ["product__name", "name", "sku"]
