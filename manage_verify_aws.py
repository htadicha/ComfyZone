#!/usr/bin/env python
"""
AWS S3 Configuration Verification Script

Run this script to verify your AWS S3 configuration:
    python manage_verify_aws.py

Or on Heroku:
    heroku run python manage_verify_aws.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'furniture_store.settings')
django.setup()

from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

def check_configuration():
    """Verify AWS S3 configuration."""
    print("=" * 60)
    print("AWS S3 Configuration Verification")
    print("=" * 60)
    print()
    
    use_aws = getattr(settings, 'USE_AWS', False)
    print(f"✓ USE_AWS: {use_aws}")
    
    if not use_aws:
        print("\n❌ AWS is not enabled! Set USE_AWS=True")
        return False
    
    print("\n📋 Configuration Values:")
    print("-" * 60)
    
    required_settings = {
        'AWS_STORAGE_BUCKET_NAME': getattr(settings, 'AWS_STORAGE_BUCKET_NAME', ''),
        'AWS_S3_REGION_NAME': getattr(settings, 'AWS_S3_REGION_NAME', ''),
        'AWS_ACCESS_KEY_ID': getattr(settings, 'AWS_ACCESS_KEY_ID', ''),
        'AWS_SECRET_ACCESS_KEY': getattr(settings, 'AWS_SECRET_ACCESS_KEY', ''),
    }
    
    optional_settings = {
        'AWS_LOCATION': getattr(settings, 'AWS_LOCATION', 'media'),
        'AWS_DEFAULT_ACL': getattr(settings, 'AWS_DEFAULT_ACL', None),
        'MEDIA_URL': getattr(settings, 'MEDIA_URL', ''),
    }
    
    missing = []
    
    for key, value in required_settings.items():
        if key in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']:
            display_value = value[:4] + '****' if value else 'NOT SET'
        else:
            display_value = value if value else 'NOT SET'
        
        status = "✓" if value else "✗"
        print(f"{status} {key}: {display_value}")
        
        if not value or (isinstance(value, str) and not value.strip()):
            missing.append(key)
    
    for key, value in optional_settings.items():
        if key == 'AWS_DEFAULT_ACL':
            display_value = str(value) if value is not None else 'None'
        else:
            display_value = value if value else 'NOT SET'
        status = "✓" if value else "ℹ"
        print(f"{status} {key}: {display_value}")
    
    print()
    print("📝 Additional Settings:")
    print("-" * 60)
    print(f"  DEFAULT_FILE_STORAGE: {getattr(settings, 'DEFAULT_FILE_STORAGE', 'NOT SET')}")
    print(f"  AWS_S3_FILE_OVERWRITE: {getattr(settings, 'AWS_S3_FILE_OVERWRITE', False)}")
    print(f"  AWS_QUERYSTRING_AUTH: {getattr(settings, 'AWS_QUERYSTRING_AUTH', False)}")
    
    acl = getattr(settings, 'AWS_DEFAULT_ACL', None)
    print()
    print("🔐 ACL Configuration:")
    print("-" * 60)
    if acl is None:
        print("  ⚠️  AWS_DEFAULT_ACL is None")
        print("     → Objects will not be publicly readable unless bucket policy allows it")
        print("     → For public product images, consider setting AWS_DEFAULT_ACL = 'public-read'")
    elif acl == 'public-read':
        print("  ✓ AWS_DEFAULT_ACL is set to 'public-read' (good for public images)")
    else:
        print(f"  ℹ️  AWS_DEFAULT_ACL is set to '{acl}'")
    
    if missing:
        print()
        print("❌ Missing Required Configuration:")
        print("-" * 60)
        for key in missing:
            print(f"  - {key} is not set or is empty")
        print()
        print("  Please set all required configuration values before testing S3 connection.")
        return False
    
    media_url = optional_settings.get('MEDIA_URL', '')
    media_url_valid = False
    
    print()
    print("🔗 Media URL Configuration:")
    print("-" * 60)
    if not media_url:
        print("  ✗ MEDIA_URL is not set")
        print("     → This should be auto-generated from bucket name and region")
        print("     → Check your AWS configuration")
    elif media_url.startswith('https://'):
        print(f"  ✓ MEDIA_URL uses HTTPS: {media_url}")
        print("  ✓ Images will be served from S3")
        media_url_valid = True
    elif media_url.startswith('/media/'):
        print(f"  ✗ MEDIA_URL is still local: {media_url}")
        print("  → This means AWS is configured but MEDIA_URL hasn't been updated")
        print("  → Check that USE_AWS=True is set and settings are loaded correctly")
        print("  → MEDIA_URL should point to S3, not local filesystem")
    else:
        print(f"  ⚠️  MEDIA_URL: {media_url}")
        print("  → Unexpected MEDIA_URL format")
    
    if not media_url_valid:
        print()
        print("❌ MEDIA_URL Configuration Issue:")
        print("-" * 60)
        print("  MEDIA_URL must be set to an S3 URL when USE_AWS=True")
        print("  This indicates a configuration problem that will prevent images from loading.")
        print()
        print("  Possible fixes:")
        print("    1. Ensure USE_AWS=True is set")
        print("    2. Verify AWS_STORAGE_BUCKET_NAME and AWS_S3_REGION_NAME are correct")
        print("    3. Check that Django settings are loading AWS configuration correctly")
        return False
    
    print()
    print("🔌 Testing S3 Connection:")
    print("-" * 60)
    try:
        storage = S3Boto3Storage()
        storage.listdir('')
        print("  ✓ S3 connection successful!")
        print("  ✓ Credentials are valid")
        print("  ✓ Bucket access is working")
    except Exception as e:
        print(f"  ❌ S3 connection failed!")
        print(f"     Error: {str(e)}")
        print()
        print("  Troubleshooting:")
        print("    - Check AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        print("    - Verify IAM user has s3:ListBucket permission")
        print("    - Confirm bucket name and region are correct")
        return False
    
    print()
    print("=" * 60)
    print("✅ Configuration Check Complete!")
    print("=" * 60)
    
    if acl is None:
        print()
        print("💡 Recommendation:")
        print("   For public product images, consider setting AWS_DEFAULT_ACL = 'public-read'")
        print("   OR ensure your S3 bucket has a bucket policy that allows public read access.")
    
    return True

if __name__ == '__main__':
    try:
        success = check_configuration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

