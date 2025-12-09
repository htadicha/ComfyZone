from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.conf import settings


class Category(models.Model):
    """Product category model with parent-child relationship."""
    
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children"
    )
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        """Return the category name."""
        return self.name

    def save(self, *args, **kwargs):
        """Generate slug before saving the category."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Return the category detail URL."""
        return reverse("store:category", kwargs={"slug": self.slug})

    def get_full_path(self):
        """Get full category path including parent categories."""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name


class ProductManager(models.Manager):
    """Custom manager for Product model."""
    
    def active(self):
        """Return active products with stock available."""
        return self.filter(is_active=True, stock__gt=0)

    def in_stock(self):
        """Return products currently in stock."""
        return self.filter(stock__gt=0)

    def out_of_stock(self):
        """Return products with zero stock."""
        return self.filter(stock=0)


class Product(models.Model):
    """Product model."""
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="products")
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    compare_at_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Original price for showing discounts"
    )
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(max_length=300, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProductManager()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        """Return the product name."""
        return self.name

    def save(self, *args, **kwargs):
        """Populate slug and SKU before saving the product."""
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.sku:
            base_sku = slugify(self.name).upper()[:8]
            self.sku = f"{base_sku}-{self.id}" if self.id else base_sku
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Return the product detail URL."""
        return reverse("store:product_detail", kwargs={"slug": self.slug})

    def is_in_stock(self):
        """Return True when stock is greater than zero."""
        return self.stock > 0

    def get_discount_percentage(self):
        """Calculate discount percentage if compare_at_price exists."""
        if self.compare_at_price and self.compare_at_price > self.price:
            discount = ((self.compare_at_price - self.price) / self.compare_at_price) * 100
            return round(discount, 0)
        return 0

    def get_primary_image(self):
        """Get the primary product image."""
        return self.images.filter(is_primary=True).first() or self.images.first()

    def get_average_rating(self):
        """Get average rating from reviews."""
        from reviews.models import Review
        from django.db.models import Avg
        reviews = Review.objects.filter(product=self, is_approved=True)
        if reviews.exists():
            return round(reviews.aggregate(Avg("rating"))["rating__avg"] or 0, 1)
        return 0

    def get_review_count(self):
        """Get total review count."""
        from reviews.models import Review
        return Review.objects.filter(product=self, is_approved=True).count()


class ProductImage(models.Model):
    """Product image model."""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="photos/products/")
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["is_primary", "order", "created_at"]

    def __str__(self):
        """Return a label for the product image."""
        return f"{self.product.name} - Image {self.id}"

    def save(self, *args, **kwargs):
        """Ensure only one primary image per product before saving."""
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).exclude(
                pk=self.pk
            ).update(is_primary=False)
        super().save(*args, **kwargs)


class ProductVariation(models.Model):
    """Product variation model (color, size, material, etc.)."""
    
    VARIATION_TYPE_CHOICES = [
        ("color", "Color"),
        ("size", "Size"),
        ("material", "Material"),
        ("style", "Style"),
        ("other", "Other"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variations")
    variation_type = models.CharField(max_length=20, choices=VARIATION_TYPE_CHOICES)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100, blank=True)
    price_adjustment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Additional price for this variation (can be negative)"
    )
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["product", "variation_type", "name"]
        ordering = ["variation_type", "name"]

    def __str__(self):
        """Return the variation label for the product."""
        return f"{self.product.name} - {self.variation_type}: {self.name}"

    def get_final_price(self):
        """Get final price including variation adjustment."""
        return self.product.price + self.price_adjustment


@receiver(post_save, sender=ProductImage)
def set_s3_acl_on_product_image(sender, instance, created, **kwargs):
    """Ensure S3 images receive public-read ACL after saves when AWS is enabled."""
    if not getattr(settings, "USE_AWS", False) or not instance.image:
        return

    import threading
    import time
    import boto3
    from botocore.exceptions import ClientError
    import logging

    logger = logging.getLogger(__name__)
    normalized_name = instance.image.name

    def set_acl_after_delay():
        """Set ACL after a short delay to ensure file is uploaded."""
        time.sleep(1)

        try:
            bucket_name = getattr(settings, "AWS_STORAGE_BUCKET_NAME", "")
            region_name = getattr(settings, "AWS_S3_REGION_NAME", "")
            aws_access_key_id = getattr(settings, "AWS_ACCESS_KEY_ID", "")
            aws_secret_access_key = getattr(settings, "AWS_SECRET_ACCESS_KEY", "")

            if not all([bucket_name, region_name, aws_access_key_id, aws_secret_access_key]):
                logger.warning("Signal: AWS settings not complete, skipping ACL setting")
                return

            storage = instance.image.storage
            image_name = instance.image.name

            logger.info(
                "Signal: Processing image",
                extra={"name": image_name, "storage": storage.__class__.__name__},
            )

            if hasattr(storage, "location") and storage.location:
                location = storage.location.strip("/") if storage.location else ""
            else:
                location = getattr(settings, "AWS_LOCATION", "media").strip("/")

            if location.startswith("app/"):
                location = location[4:]

            if image_name.startswith("app/media/"):
                image_name = image_name[10:]
            elif image_name.startswith("app/"):
                image_name = image_name[4:]

            normalized_name = image_name.lstrip("/")
            if hasattr(storage, "_normalize_name") and hasattr(storage, "_clean_name"):
                try:
                    normalized_name = storage._normalize_name(storage._clean_name(image_name))
                except Exception:
                    normalized_name = image_name.lstrip("/")

            if normalized_name.startswith(f"{location}/"):
                s3_key = normalized_name
            elif normalized_name.startswith("/"):
                s3_key = f"{location}{normalized_name}"
            else:
                s3_key = f"{location}/{normalized_name}" if location else normalized_name

            s3_client = boto3.client(
                "s3",
                region_name=region_name,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
            )

            clean_image_name = image_name
            if clean_image_name.startswith("app/media/"):
                clean_image_name = clean_image_name[10:]
            elif clean_image_name.startswith("app/"):
                clean_image_name = clean_image_name[4:]

            possible_keys = [
                s3_key,
                clean_image_name,
                image_name,
                f"{location}/{clean_image_name}",
                f"{location}/{image_name}",
                f"media/{clean_image_name}",
                f"media/{image_name}",
                f"/{clean_image_name}",
                f"/{image_name}",
                f"{location}{clean_image_name}",
                f"{location}{image_name}",
            ]

            seen = set()
            unique_keys = []
            for key in possible_keys:
                if key not in seen:
                    seen.add(key)
                    unique_keys.append(key)

            logger.error(
                "Signal: S3 key resolution debug",
                extra={
                    "image_name_original": instance.image.name,
                    "image_name_cleaned": image_name,
                    "normalized_name": normalized_name,
                    "location": location,
                    "constructed_s3_key": s3_key,
                    "possible_keys": possible_keys,
                    "unique_keys": unique_keys,
                    "bucket": bucket_name,
                },
            )

            file_found = False
            for key in unique_keys:
                try:
                    logger.info(
                        "Signal: head_object check",
                        extra={"bucket": bucket_name, "key": key},
                    )
                    s3_client.head_object(Bucket=bucket_name, Key=key)
                    file_found = True
                    logger.error(
                        "Signal: File found; attempting ACL",
                        extra={"key": key, "bucket": bucket_name},
                    )

                    try:
                        logger.info(
                            "Signal: put_object_acl public-read",
                            extra={"bucket": bucket_name, "key": key},
                        )
                        s3_client.put_object_acl(
                            Bucket=bucket_name,
                            Key=key,
                            ACL="public-read",
                        )
                        logger.info("Signal: Set ACL to public-read for %s", key)
                        break
                    except ClientError as e:
                        error_code = e.response.get("Error", {}).get("Code", "")
                        if "BlockPublicAccess" in str(e) or error_code == "AccessDenied":
                            logger.error(
                                "Signal: Cannot set ACL for %s", key,
                                extra={"error": str(e)},
                            )
                        else:
                            logger.warning(
                                "Signal: Could not set ACL for %s", key,
                                extra={"error": str(e)},
                            )
                    break
                except ClientError as e:
                    if e.response["Error"]["Code"] != "404":
                        logger.warning(
                            "Signal: Error checking file %s", key,
                            extra={"error": str(e)},
                        )
                    continue

            if not file_found:
                logger.warning(
                    "Signal: File not found in S3 for keys",
                    extra={"keys": unique_keys},
                )

        except Exception as e:
            logger.error(f"Error setting S3 ACL for product image: {e}")
            import traceback
            logger.error(traceback.format_exc())

    thread = threading.Thread(target=set_acl_after_delay)
    thread.daemon = True
    thread.start()
