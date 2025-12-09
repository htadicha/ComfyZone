#!/usr/bin/env python
"""
Script to fix ACL on existing S3 product images.
This makes all product images publicly accessible.

Run this script after deploying the MediaStorage fix:
    python fix_s3_acl.py

Or on Heroku:
    heroku run python fix_s3_acl.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'furniture_store.settings')
django.setup()

from django.conf import settings
from store.models import ProductImage
import boto3
from botocore.exceptions import ClientError

print("=" * 60)
print("Fix S3 ACL for Product Images")
print("=" * 60)
print()

if not getattr(settings, 'USE_AWS', False):
    print("❌ AWS is not enabled!")
    print("   This script only works when USE_AWS=True")
    sys.exit(1)

# Get AWS settings
bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', '')
region_name = getattr(settings, 'AWS_S3_REGION_NAME', '')
aws_access_key_id = getattr(settings, 'AWS_ACCESS_KEY_ID', '')
aws_secret_access_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', '')

if not all([bucket_name, region_name, aws_access_key_id, aws_secret_access_key]):
    print("❌ Missing required AWS configuration!")
    sys.exit(1)

# Initialize S3 client
s3_client = boto3.client(
    's3',
    region_name=region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

# Get all product images
images = ProductImage.objects.all()

if not images:
    print("No product images found in database.")
    sys.exit(0)

print(f"Found {images.count()} product image(s) in database.\n")
print("Fixing ACL on S3 files...\n")

fixed_count = 0
error_count = 0

for img in images:
    # Get the S3 key (path) for this image
    image_name = img.image.name
    aws_location = getattr(settings, 'AWS_LOCATION', 'media')
    
    # Construct the S3 key
    # The image.name already includes the upload_to path (photos/products/)
    # and AWS_LOCATION is the prefix
    s3_key = f"{aws_location}/{image_name}" if not image_name.startswith(aws_location) else image_name
    
    print(f"Product: {img.product.name}")
    print(f"  S3 Key: {s3_key}")
    print(f"  URL: {img.image.url}")
    
    try:
        # Check if file exists
        try:
            s3_client.head_object(Bucket=bucket_name, Key=s3_key)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                print(f"  ⚠️  File not found in S3, skipping...")
                error_count += 1
                print()
                continue
            else:
                raise
        
        # Set ACL to public-read
        s3_client.put_object_acl(
            Bucket=bucket_name,
            Key=s3_key,
            ACL='public-read'
        )
        print(f"  ✅ ACL set to 'public-read'")
        fixed_count += 1
    except ClientError as e:
        print(f"  ❌ Error: {e}")
        error_count += 1
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        error_count += 1
    
    print()

print("=" * 60)
print("Summary:")
print(f"  ✅ Fixed: {fixed_count}")
print(f"  ❌ Errors: {error_count}")
print("=" * 60)
print()
print("💡 Note: New uploads will automatically have 'public-read' ACL")
print("   thanks to the MediaStorage class fix.")

