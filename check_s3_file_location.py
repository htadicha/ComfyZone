#!/usr/bin/env python
"""
Script to check where files are actually stored in S3
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'furniture_store.settings')
django.setup()

from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from store.models import ProductImage

print("=" * 60)
print("S3 File Location Checker")
print("=" * 60)
print()

if not getattr(settings, 'USE_AWS', False):
    print("❌ AWS is not enabled!")
    sys.exit(1)

print("📋 Current Configuration:")
print("-" * 60)
print(f"AWS_STORAGE_BUCKET_NAME: {getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'NOT SET')}")
print(f"AWS_S3_REGION_NAME: {getattr(settings, 'AWS_S3_REGION_NAME', 'NOT SET')}")
print(f"AWS_LOCATION: {getattr(settings, 'AWS_LOCATION', 'media')}")
print(f"MEDIA_URL: {getattr(settings, 'MEDIA_URL', 'NOT SET')}")
print()

print("📸 Product Images in Database:")
print("-" * 60)
images = ProductImage.objects.all()[:10]  # First 10 images

if not images:
    print("  No product images found in database.")
else:
    storage = S3Boto3Storage()
    print(f"  Found {ProductImage.objects.count()} total images. Showing first {len(images)}:\n")
    
    for img in images:
        print(f"  Product: {img.product.name}")
        print(f"    Image field value: {img.image.name}")
        print(f"    Image URL: {img.image.url}")
        print(f"    Full path in S3: {storage.location}/{img.image.name}")
        
        try:
            exists = storage.exists(img.image.name)
            print(f"    ✓ File exists in S3: {exists}")
        except Exception as e:
            print(f"    ✗ Error checking file: {e}")
        print()

print("🔍 Files in S3 Bucket:")
print("-" * 60)
try:
    storage = S3Boto3Storage()
    files, dirs = storage.listdir('media/products/')
    
    if files:
        print(f"  Found {len(files)} files in media/products/:")
        for f in files[:10]:  # Show first 10
            print(f"    - {f}")
        if len(files) > 10:
            print(f"    ... and {len(files) - 10} more")
    else:
        print("  No files found in media/products/")
        print("  Checking root media/ directory...")
        files, dirs = storage.listdir('media/')
        print(f"  Found {len(dirs)} directories and {len(files)} files in media/:")
        for d in dirs:
            print(f"    📁 {d}/")
        for f in files[:10]:
            print(f"    📄 {f}")
            
except Exception as e:
    print(f"  ❌ Error listing files: {e}")
    print(f"  Error type: {type(e).__name__}")

print()
print("=" * 60)
print("💡 Troubleshooting:")
print("=" * 60)
print()
print("If files are in a different location:")
print("  1. Check AWS_LOCATION setting")
print("  2. Verify upload_to path in ProductImage model")
print("  3. Check if files were uploaded to a different bucket/path")
print()
print("If no files found:")
print("  1. Images may not have been uploaded yet")
print("  2. Check IAM permissions (s3:ListBucket, s3:GetObject)")
print("  3. Verify bucket name is correct")





