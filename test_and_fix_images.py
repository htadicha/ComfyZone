#!/usr/bin/env python
"""
Test image URLs and fix any issues.
"""
import os
import sys
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'furniture_store.settings')
django.setup()

from django.conf import settings
from store.models import ProductImage
import boto3
from botocore.exceptions import ClientError

print("=" * 70)
print("Image URL Test and Fix Script")
print("=" * 70)
print()

if not getattr(settings, 'USE_AWS', False):
    print("❌ AWS is not enabled!")
    sys.exit(1)

bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', '')
region_name = getattr(settings, 'AWS_S3_REGION_NAME', '')
aws_access_key_id = getattr(settings, 'AWS_ACCESS_KEY_ID', '')
aws_secret_access_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', '')
aws_location = getattr(settings, 'AWS_LOCATION', 'media').strip('/')

s3_client = boto3.client(
    's3',
    region_name=region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

images = ProductImage.objects.all()
print(f"Testing {images.count()} product images...\n")

fixed = 0
working = 0
broken = 0

for img in images:
    image_name = img.image.name
    url = img.image.url
    
    # Construct S3 key
    if image_name.startswith(aws_location + '/'):
        s3_key = image_name
    elif image_name.startswith('/'):
        s3_key = f"{aws_location}{image_name}"
    else:
        s3_key = f"{aws_location}/{image_name}"
    
    print(f"📸 {img.product.name}")
    print(f"   URL: {url}")
    print(f"   S3 Key: {s3_key}")
    
    # Check if file exists
    try:
        s3_client.head_object(Bucket=bucket_name, Key=s3_key)
        file_exists = True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"   ❌ File NOT FOUND in S3")
            broken += 1
            print()
            continue
        else:
            print(f"   ❌ Error: {e}")
            broken += 1
            print()
            continue
    
    # Check ACL
    try:
        acl_response = s3_client.get_object_acl(Bucket=bucket_name, Key=s3_key)
        grants = acl_response.get('Grants', [])
        
        public_read = any(
            grant.get('Grantee', {}).get('URI') == 'http://acs.amazonaws.com/groups/global/AllUsers'
            and grant.get('Permission') == 'READ'
            for grant in grants
        )
        
        if not public_read:
            print(f"   ⚠️  ACL is NOT public-read, fixing...")
            try:
                s3_client.put_object_acl(
                    Bucket=bucket_name,
                    Key=s3_key,
                    ACL='public-read'
                )
                print(f"   ✅ Fixed ACL")
                fixed += 1
            except Exception as e:
                print(f"   ❌ Failed to fix ACL: {e}")
                broken += 1
        else:
            print(f"   ✅ ACL is public-read")
        
        # Test URL accessibility
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                print(f"   ✅ URL is accessible (HTTP {response.status_code})")
                working += 1
            elif response.status_code == 403:
                print(f"   ❌ URL returns 403 Forbidden")
                print(f"      → File exists but access is denied")
                broken += 1
            else:
                print(f"   ⚠️  URL returns HTTP {response.status_code}")
                broken += 1
        except requests.exceptions.RequestException as e:
            print(f"   ⚠️  Could not test URL: {e}")
            # But file exists and ACL is correct, so assume it works
            if public_read:
                working += 1
            else:
                broken += 1
                
    except Exception as e:
        print(f"   ❌ Error checking ACL: {e}")
        broken += 1
    
    print()

print("=" * 70)
print("Summary")
print("=" * 70)
print(f"  ✅ Working: {working}")
print(f"  ✅ Fixed: {fixed}")
print(f"  ❌ Broken: {broken}")
print(f"  📊 Total: {images.count()}")
print()

if broken > 0:
    print("⚠️  Some images are still broken.")
    print("   Common causes:")
    print("   1. File doesn't exist in S3 (needs re-upload)")
    print("   2. Block Public Access is enabled on bucket")
    print("   3. Bucket policy blocks access")
    print("   4. CORS issues")
print("=" * 70)

