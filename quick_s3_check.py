#!/usr/bin/env python
"""Quick check: Does the specific file exist in S3?"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'furniture_store.settings')
django.setup()

from storages.backends.s3boto3 import S3Boto3Storage
from store.models import ProductImage

print("Checking for file: media/products/16216048_rm405-c02a.jpg")
print("=" * 60)

storage = S3Boto3Storage()

# Check if file exists
file_path = "media/products/16216048_rm405-c02a.jpg"
exists = storage.exists(file_path)
print(f"\n✓ File exists in S3: {exists}")

if not exists:
    print("\n❌ File NOT found at that path!")
    print("\nChecking database for this image...")
    
    # Find in database
    images = ProductImage.objects.all()
    for img in images:
        if '16216048_rm405-c02a' in str(img.image):
            print(f"\nFound in database:")
            print(f"  Image field: {img.image.name}")
            print(f"  Full URL: {img.image.url}")
            
            # Check actual S3 path
            actual_exists = storage.exists(img.image.name)
            print(f"  Exists at actual path: {actual_exists}")
            break
    
    print("\nListing files in media/products/...")
    try:
        files, dirs = storage.listdir("media/products/")
        if files:
            print(f"\nFound {len(files)} files. Showing first 10:")
            for f in files[:10]:
                print(f"  - {f}")
        else:
            print("\n⚠️  No files found in media/products/")
            print("Checking media/ root...")
            files, dirs = storage.listdir("media/")
            print(f"Found {len(dirs)} directories:")
            for d in dirs:
                print(f"  📁 {d}/")
    except Exception as e:
        print(f"\n❌ Error listing files: {e}")

else:
    print("\n✅ File EXISTS! Check permissions/bucket policy instead.")
    print("The issue is likely bucket permissions, not file location.")

