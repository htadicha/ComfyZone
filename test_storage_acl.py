#!/usr/bin/env python
"""
Test script to verify that MediaStorage is correctly setting ACL on uploads.
"""
import os
import sys
import django
from io import BytesIO
from PIL import Image

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'furniture_store.settings')
django.setup()

from django.conf import settings
from furniture_store.storage import MediaStorage
import boto3
from botocore.exceptions import ClientError

print("=" * 60)
print("Testing MediaStorage ACL Configuration")
print("=" * 60)
print()

if not getattr(settings, 'USE_AWS', False):
    print("❌ AWS is not enabled!")
    sys.exit(1)

# Check settings
print("📋 Configuration Check:")
print("-" * 60)
print(f"AWS_DEFAULT_ACL: {getattr(settings, 'AWS_DEFAULT_ACL', 'NOT SET')}")
print(f"DEFAULT_FILE_STORAGE: {getattr(settings, 'DEFAULT_FILE_STORAGE', 'NOT SET')}")
print()

# Initialize storage
storage = MediaStorage()
print(f"Storage class: {storage.__class__.__name__}")
print(f"Storage default_acl: {getattr(storage, 'default_acl', 'NOT SET')}")
print()

# Test creating a small test image
print("🧪 Testing ACL on upload:")
print("-" * 60)

try:
    # Create a small test image
    img = Image.new('RGB', (100, 100), color='red')
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    # Upload test file
    test_filename = 'test_acl_check.png'
    print(f"Uploading test file: {test_filename}")
    
    saved_name = storage.save(test_filename, img_buffer)
    print(f"✅ File saved as: {saved_name}")
    
    # Check ACL on the uploaded file
    print(f"\nChecking ACL on uploaded file...")
    
    # Get S3 client
    s3_client = boto3.client(
        's3',
        region_name=getattr(settings, 'AWS_S3_REGION_NAME', ''),
        aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', ''),
        aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', '')
    )
    
    bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', '')
    aws_location = getattr(settings, 'AWS_LOCATION', 'media')
    s3_key = f"{aws_location}/{saved_name}" if not saved_name.startswith(aws_location) else saved_name
    
    # Get object ACL
    try:
        acl_response = s3_client.get_object_acl(Bucket=bucket_name, Key=s3_key)
        grants = acl_response.get('Grants', [])
        
        print(f"  S3 Key: {s3_key}")
        print(f"  ACL Grants:")
        public_read = False
        for grant in grants:
            grantee = grant.get('Grantee', {})
            permission = grant.get('Permission', '')
            if grantee.get('Type') == 'Group' and grantee.get('URI') == 'http://acs.amazonaws.com/groups/global/AllUsers':
                if permission == 'READ':
                    public_read = True
                    print(f"    ✅ Public READ access: {permission}")
                else:
                    print(f"    ℹ️  Public access: {permission}")
            else:
                print(f"    ℹ️  {grantee.get('Type', 'Unknown')}: {permission}")
        
        if public_read:
            print(f"\n  ✅ SUCCESS: File has public-read ACL!")
        else:
            print(f"\n  ❌ WARNING: File does NOT have public-read ACL!")
            print(f"     This means the storage class is not setting ACL correctly.")
        
        # Try to access the file URL
        file_url = storage.url(saved_name)
        print(f"\n  File URL: {file_url}")
        print(f"  Try accessing this URL in a browser to verify it's publicly accessible.")
        
    except ClientError as e:
        print(f"  ❌ Error checking ACL: {e}")
    
    # Clean up test file
    print(f"\nCleaning up test file...")
    try:
        storage.delete(saved_name)
        print(f"  ✅ Test file deleted")
    except Exception as e:
        print(f"  ⚠️  Could not delete test file: {e}")
        print(f"     You may need to delete it manually: {s3_key}")
    
except Exception as e:
    print(f"❌ Error during test: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("Test Complete")
print("=" * 60)

