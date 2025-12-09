#!/usr/bin/env python
"""
Comprehensive S3 diagnostic script to identify why images are broken.
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
print("S3 Image Access Diagnostic Tool")
print("=" * 70)
print()

# Check 1: AWS Configuration
print("1️⃣  AWS Configuration Check")
print("-" * 70)
use_aws = getattr(settings, 'USE_AWS', False)
print(f"   USE_AWS: {use_aws}")

if not use_aws:
    print("   ❌ AWS is not enabled!")
    print("   → Set USE_AWS=True in your environment variables")
    sys.exit(1)

bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', '')
region_name = getattr(settings, 'AWS_S3_REGION_NAME', '')
aws_access_key_id = getattr(settings, 'AWS_ACCESS_KEY_ID', '')
aws_secret_access_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', '')
aws_location = getattr(settings, 'AWS_LOCATION', 'media')
aws_default_acl = getattr(settings, 'AWS_DEFAULT_ACL', None)
default_file_storage = getattr(settings, 'DEFAULT_FILE_STORAGE', '')

print(f"   AWS_STORAGE_BUCKET_NAME: {bucket_name}")
print(f"   AWS_S3_REGION_NAME: {region_name}")
print(f"   AWS_LOCATION: {aws_location}")
print(f"   AWS_DEFAULT_ACL: {aws_default_acl}")
print(f"   DEFAULT_FILE_STORAGE: {default_file_storage}")

if not all([bucket_name, region_name, aws_access_key_id, aws_secret_access_key]):
    print("   ❌ Missing required AWS credentials!")
    sys.exit(1)

if aws_default_acl != 'public-read':
    print("   ⚠️  AWS_DEFAULT_ACL is not set to 'public-read'")
    print("   → This should be 'public-read' for public images")

if 'MediaStorage' not in default_file_storage:
    print("   ⚠️  DEFAULT_FILE_STORAGE is not using MediaStorage")
    print("   → Should be 'furniture_store.storage.MediaStorage'")

print()

# Check 2: S3 Connection
print("2️⃣  S3 Connection Test")
print("-" * 70)
try:
    s3_client = boto3.client(
        's3',
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    
    # Test connection by listing bucket
    s3_client.head_bucket(Bucket=bucket_name)
    print("   ✅ S3 connection successful")
    print("   ✅ Bucket exists and is accessible")
except ClientError as e:
    error_code = e.response.get('Error', {}).get('Code', '')
    if error_code == '403':
        print("   ❌ Access Denied - Check IAM permissions")
    elif error_code == '404':
        print("   ❌ Bucket not found - Check bucket name")
    else:
        print(f"   ❌ Connection failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ Unexpected error: {e}")
    sys.exit(1)

print()

# Check 3: Product Images in Database
print("3️⃣  Product Images in Database")
print("-" * 70)
images = ProductImage.objects.all()[:5]

if not images:
    print("   ⚠️  No product images found in database")
else:
    print(f"   Found {ProductImage.objects.count()} total images")
    print(f"   Checking first {len(images)} images:\n")
    
    for img in images:
        print(f"   📸 {img.product.name}")
        print(f"      Image name: {img.image.name}")
        print(f"      Image URL: {img.image.url}")
        
        # Construct S3 key
        if img.image.name.startswith(aws_location):
            s3_key = img.image.name
        else:
            s3_key = f"{aws_location}/{img.image.name}"
        
        print(f"      S3 Key: {s3_key}")
        
        # Check if file exists
        try:
            s3_client.head_object(Bucket=bucket_name, Key=s3_key)
            print(f"      ✅ File exists in S3")
            
            # Check ACL
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
                            print(f"      ✅ ACL: public-read (READ permission for Everyone)")
                        else:
                            print(f"      ⚠️  ACL: {permission} for Everyone (should be READ)")
                
                if not public_read:
                    print(f"      ❌ ACL: NOT public-read - This is the problem!")
                    print(f"      → Run: python fix_s3_acl.py")
                
            except ClientError as e:
                print(f"      ⚠️  Could not check ACL: {e}")
            
            # Try to access the file
            try:
                # Generate a presigned URL (this tests if we can access it)
                url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket_name, 'Key': s3_key},
                    ExpiresIn=60
                )
                print(f"      ✅ Can generate presigned URL (file is accessible)")
            except Exception as e:
                print(f"      ⚠️  Could not generate presigned URL: {e}")
                
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                print(f"      ❌ File NOT FOUND in S3!")
                print(f"      → File was not uploaded or path is incorrect")
            else:
                print(f"      ❌ Error checking file: {e}")
        
        print()

print()

# Check 4: Bucket Public Access Block Settings
print("4️⃣  Bucket Public Access Settings (Manual Check Required)")
print("-" * 70)
print("   ⚠️  This requires manual check in AWS Console")
print()
print("   Steps to check:")
print("   1. Go to AWS S3 Console: https://s3.console.aws.amazon.com/")
print(f"   2. Select bucket: {bucket_name}")
print("   3. Go to 'Permissions' tab")
print("   4. Scroll to 'Block public access (bucket settings)'")
print("   5. Click 'Edit'")
print("   6. ALL four checkboxes should be UNCHECKED:")
print("      ☐ Block all public access")
print("      ☐ Block public access to buckets and objects granted through new ACLs")
print("      ☐ Block public access to buckets and objects granted through any ACLs")
print("      ☐ Block public access to buckets and objects granted through new policies")
print()
print("   If any are checked, UNCHECK them and save.")
print("   ⚠️  AWS will warn you - this is expected for public product images!")
print()

# Check 5: Storage Class
print("5️⃣  Storage Class Check")
print("-" * 70)
try:
    from furniture_store.storage import MediaStorage
    storage = MediaStorage()
    print(f"   ✅ MediaStorage class imported successfully")
    print(f"   Storage default_acl: {getattr(storage, 'default_acl', 'NOT SET')}")
    
    if hasattr(storage, '_save'):
        print(f"   ✅ _save method is overridden")
    else:
        print(f"   ⚠️  _save method not overridden")
        
except ImportError as e:
    print(f"   ❌ Could not import MediaStorage: {e}")
except Exception as e:
    print(f"   ⚠️  Error checking storage class: {e}")

print()

# Check 6: Signal Registration
print("6️⃣  Signal Registration Check")
print("-" * 70)
try:
    from django.db.models.signals import post_save
    from store.models import ProductImage
    
    # Check if signal is registered
    receivers = post_save._live_receivers(ProductImage)
    signal_found = False
    for receiver in receivers:
        if 'set_s3_acl' in str(receiver):
            signal_found = True
            break
    
    if signal_found:
        print("   ✅ Post-save signal is registered")
    else:
        print("   ⚠️  Post-save signal not found")
        print("   → Make sure store.models is imported in apps.py")
        
except Exception as e:
    print(f"   ⚠️  Could not check signals: {e}")

print()

# Summary
print("=" * 70)
print("📋 SUMMARY & RECOMMENDATIONS")
print("=" * 70)
print()
print("If images are still broken, check in this order:")
print()
print("1. ✅ Verify S3 bucket 'Block Public Access' is disabled (Check #4 above)")
print("2. ✅ Run: python fix_s3_acl.py (to fix existing images)")
print("3. ✅ Upload a new test image and check if it works")
print("4. ✅ Check browser console for CORS errors")
print("5. ✅ Verify bucket policy allows public read access")
print()
print("For bucket policy, add this to your S3 bucket:")
print()
print('{')
print('  "Version": "2012-10-17",')
print('  "Statement": [')
print('    {')
print('      "Effect": "Allow",')
print('      "Principal": "*",')
print('      "Action": "s3:GetObject",')
print(f'      "Resource": "arn:aws:s3:::{bucket_name}/*"')
print('    }')
print('  ]')
print('}')
print()
print("=" * 70)

