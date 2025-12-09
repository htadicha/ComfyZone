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
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("store:category", kwargs={"slug": self.slug})

    def get_full_path(self):
        """Get full category path including parent categories."""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name


class ProductManager(models.Manager):
    """Custom manager for Product model."""
    
    def active(self):
        return self.filter(is_active=True, stock__gt=0)

    def in_stock(self):
        return self.filter(stock__gt=0)

    def out_of_stock(self):
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
    
    # SEO fields
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(max_length=300, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProductManager()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.sku:
            # Generate SKU from name and ID
            base_sku = slugify(self.name).upper()[:8]
            self.sku = f"{base_sku}-{self.id}" if self.id else base_sku
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("store:product_detail", kwargs={"slug": self.slug})

    def is_in_stock(self):
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
        return f"{self.product.name} - Image {self.id}"

    def save(self, *args, **kwargs):
        if self.is_primary:
            # Unset other primary images for this product
            ProductImage.objects.filter(product=self.product, is_primary=True).exclude(
                pk=self.pk
            ).update(is_primary=False)
        super().save(*args, **kwargs)
        # ACL will be set by post_save signal if using AWS


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
    name = models.CharField(max_length=100)  # e.g., "Red", "Large", "Leather"
    value = models.CharField(max_length=100, blank=True)  # e.g., "#FF0000" for color
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
        return f"{self.product.name} - {self.variation_type}: {self.name}"

    def get_final_price(self):
        """Get final price including variation adjustment."""
        return self.product.price + self.price_adjustment


@receiver(post_save, sender=ProductImage)
def set_s3_acl_on_product_image(sender, instance, created, **kwargs):
    """
    Signal to ensure S3 ACL is set to public-read after ProductImage is saved.
    This is a backup to ensure ACL is set even if storage class fails.
    Uses a small delay to allow file upload to complete.
    """
    if not getattr(settings, 'USE_AWS', False):
        return
    
    if not instance.image:
        return
    
    # Import threading for delayed execution
    import threading
    import time
    import boto3
    from botocore.exceptions import ClientError
    import logging
    
    logger = logging.getLogger(__name__)
    
    def set_acl_after_delay():
        """Set ACL after a short delay to ensure file is uploaded."""
        # Wait a bit for the file to be fully uploaded
        time.sleep(1)
        
        try:
            # Get AWS settings
            bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', '')
            region_name = getattr(settings, 'AWS_S3_REGION_NAME', '')
            aws_access_key_id = getattr(settings, 'AWS_ACCESS_KEY_ID', '')
            aws_secret_access_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', '')
            
            if not all([bucket_name, region_name, aws_access_key_id, aws_secret_access_key]):
                logger.warning("Signal: AWS settings not complete, skipping ACL setting")
                return
            
            # Use the storage class to get the correct S3 key
            storage = instance.image.storage
            image_name = instance.image.name
            
            logger.info(f"Signal: Processing image - name: {image_name}, storage: {storage.__class__.__name__}")
            
            # Get location from storage or settings
            if hasattr(storage, 'location') and storage.location:
                location = storage.location.strip('/') if storage.location else ''
            else:
                location = getattr(settings, 'AWS_LOCATION', 'media').strip('/')
            
            # Remove 'app/' prefix from location if present (common Heroku issue)
            if location.startswith('app/'):
                location = location[4:]
            
            # Remove 'app/' prefix if present in image name (common Heroku issue)
            # Also handle 'app/media/' prefix
            if image_name.startswith('app/media/'):
                image_name = image_name[10:]  # Remove 'app/media/'
            elif image_name.startswith('app/'):
                image_name = image_name[4:]  # Remove 'app/'
            
            # Get the actual S3 key from the storage class
            # Try to use storage's normalization methods
            try:
                if hasattr(storage, '_normalize_name') and hasattr(storage, '_clean_name'):
                    normalized_name = storage._normalize_name(storage._clean_name(image_name))
                else:
                    normalized_name = image_name.lstrip('/')
                
                # Construct S3 key - location + normalized name
                if normalized_name.startswith(location + '/'):
                    s3_key = normalized_name
                elif normalized_name.startswith('/'):
                    s3_key = f"{location}{normalized_name}"
                else:
                    s3_key = f"{location}/{normalized_name}" if location else normalized_name
            except:
                # Fallback to simple construction
                if image_name.startswith(location + '/'):
                    s3_key = image_name
                elif image_name.startswith('/'):
                    s3_key = f"{location}{image_name}"
                else:
                    s3_key = f"{location}/{image_name}"
            
            # Initialize S3 client
            s3_client = boto3.client(
                's3',
                region_name=region_name,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )
            
            # Try multiple key variations in case of path issues
            # Remove 'app/media/' if still present
            clean_image_name = image_name
            if clean_image_name.startswith('app/media/'):
                clean_image_name = clean_image_name[10:]
            elif clean_image_name.startswith('app/'):
                clean_image_name = clean_image_name[4:]
            
            possible_keys = [
                s3_key,
                clean_image_name,  # Cleaned name without location
                image_name,  # Original name without location
                f"{location}/{clean_image_name}",  # Location + cleaned name
                f"{location}/{image_name}",  # Location + original name
                f"media/{clean_image_name}",  # Explicit media/ check
                f"media/{image_name}",  # Explicit media/ check
                f"/{clean_image_name}",  # With leading slash
                f"/{image_name}",  # Original with leading slash
                f"{location}{clean_image_name}",  # Location without slash
                f"{location}{image_name}",  # Original location without slash
            ]
            
            # Remove duplicates while preserving order
            seen = set()
            unique_keys = []
            for key in possible_keys:
                if key not in seen:
                    seen.add(key)
                    unique_keys.append(key)
            
            # Try to find the file and set ACL
            file_found = False
            for key in unique_keys:
                try:
                    # Check if file exists
                    s3_client.head_object(Bucket=bucket_name, Key=key)
                    file_found = True
                    
                    # File exists, now set ACL to public-read
                    try:
                        s3_client.put_object_acl(
                            Bucket=bucket_name,
                            Key=key,
                            ACL='public-read'
                        )
                        logger.info(f"Signal: Set ACL to public-read for {key}")
                        break  # Success, no need to try other keys
                    except ClientError as e:
                        error_code = e.response.get('Error', {}).get('Code', '')
                        if 'BlockPublicAccess' in str(e) or error_code == 'AccessDenied':
                            logger.error(f"Signal: Cannot set ACL for {key}: Block Public Access may be enabled or IAM permissions missing")
                        else:
                            logger.warning(f"Signal: Could not set ACL for {key}: {e}")
                    break  # Found file, stop trying other keys
                except ClientError as e:
                    if e.response['Error']['Code'] != '404':
                        # Not a 404, some other error
                        logger.warning(f"Signal: Error checking file {key}: {e}")
                    continue
            
            if not file_found:
                logger.warning(f"Signal: File not found in S3 for any of these keys: {unique_keys}. Upload may have failed or path is incorrect.")
                
        except Exception as e:
            # Don't fail the save if ACL setting fails
            logger.error(f"Error setting S3 ACL for product image: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    # Run ACL setting in a separate thread with a delay
    thread = threading.Thread(target=set_acl_after_delay)
    thread.daemon = True
    thread.start()
