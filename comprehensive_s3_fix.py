#!/usr/bin/env python
"""
Comprehensive S3 fix script that:
1. Checks all product images
2. Verifies ACL on each file
3. Fixes ACL if needed
4. Reports any issues
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

print("=" * 70)
print("Comprehensive S3 ACL Fix Script")
print("=" * 70)
print()

if not getattr(settings, 'USE_AWS', False):
    print("❌ AWS is not enabled!")
    print("   This script requires USE_AWS=True")
    sys.exit(1)

# Get AWS settings
bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', '')
region_name = getattr(settings, 'AWS_S3_REGION_NAME', '')
aws_access_key_id = getattr(settings, 'AWS_ACCESS_KEY_ID', '')
aws_secret_access_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', '')
aws_location = getattr(settings, 'AWS_LOCATION', 'media').strip('/')

if not all([bucket_name, region_name, aws_access_key_id, aws_secret_access_key]):
    print("❌ Missing required AWS configuration!")
    sys.exit(1)

print(f"Configuration:")
print(f"  Bucket: {bucket_name}")
print(f"  Region: {region_name}")
print(f"  Location: {aws_location}")
print()

# Initialize S3 client
try:
    s3_client = boto3.client(
        's3',
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    
    # Test connection
    s3_client.head_bucket(Bucket=bucket_name)
    print("✅ S3 connection successful\n")
except Exception as e:
    print(f"❌ S3 connection failed: {e}")
    sys.exit(1)

# Get all product images
images = ProductImage.objects.all()

if not images:
    print("No product images found in database.")
    sys.exit(0)

print(f"Found {images.count()} product image(s)\n")
print("Checking and fixing ACL...\n")
print("-" * 70)

fixed_count = 0
already_public_count = 0
error_count = 0
not_found_count = 0

for img in images:
    image_name = img.image.name
    product_name = img.product.name
    
    # Construct S3 key - handle different formats
    if image_name.startswith(aws_location + '/'):
        s3_key = image_name
    elif image_name.startswith('/'):
        s3_key = f"{aws_location}{image_name}"
    else:
        s3_key = f"{aws_location}/{image_name}"
    
    print(f"\n📸 {product_name}")
    print(f"   Image name: {image_name}")
    print(f"   S3 Key: {s3_key}")
    print(f"   URL: {img.image.url}")
    
    # Check if file exists
    try:
        s3_client.head_object(Bucket=bucket_name, Key=s3_key)
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"   ❌ File NOT FOUND in S3!")
            not_found_count += 1
            continue
        else:
            print(f"   ❌ Error checking file: {e}")
            error_count += 1
            continue
    
    # Check current ACL
    try:
        acl_response = s3_client.get_object_acl(Bucket=bucket_name, Key=s3_key)
        grants = acl_response.get('Grants', [])
        
        public_read = False
        for grant in grants:
            grantee = grant.get('Grantee', {})
            permission = grant.get('Permission', '')
            if grantee.get('Type') == 'Group' and grantee.get('URI') == 'http://acs.amazonaws.com/groups/global/AllUsers':
                if permission == 'READ':
                    public_read = True
                    break
        
        if public_read:
            print(f"   ✅ Already has public-read ACL")
            already_public_count += 1
        else:
            # Fix ACL
            try:
                s3_client.put_object_acl(
                    Bucket=bucket_name,
                    Key=s3_key,
                    ACL='public-read'
                )
                print(f"   ✅ Fixed: Set ACL to public-read")
                fixed_count += 1
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', '')
                if error_code == 'AccessDenied':
                    print(f"   ❌ Access Denied - Check IAM permissions")
                elif 'BlockPublicAccess' in str(e):
                    print(f"   ❌ Block Public Access is enabled on bucket!")
                    print(f"      → Disable it in S3 Console → Bucket → Permissions")
                else:
                    print(f"   ❌ Error setting ACL: {e}")
                error_count += 1
                
    except ClientError as e:
        print(f"   ❌ Error checking ACL: {e}")
        error_count += 1

print()
print("=" * 70)
print("Summary")
print("=" * 70)
print(f"  ✅ Already public: {already_public_count}")
print(f"  ✅ Fixed: {fixed_count}")
print(f"  ❌ Errors: {error_count}")
print(f"  ❌ Not found: {not_found_count}")
print(f"  📊 Total: {images.count()}")
print()

if error_count > 0:
    print("⚠️  Some errors occurred. Common issues:")
    print("   1. Block Public Access is enabled on bucket")
    print("   2. IAM user lacks s3:PutObjectAcl permission")
    print("   3. Bucket policy blocks ACL changes")
    print()

if not_found_count > 0:
    print("⚠️  Some files were not found in S3.")
    print("   These images may need to be re-uploaded.")
    print()

print("=" * 70)

