#!/usr/bin/env python
"""Check where AWS configuration is being read from"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'furniture_store.settings')
django.setup()

from django.conf import settings

print("=" * 60)
print("AWS Configuration Source Checker")
print("=" * 60)
print()

print("🔍 Checking Environment Variables:")
print("-" * 60)
aws_vars = [
    'USE_AWS',
    'AWS_STORAGE_BUCKET_NAME',
    'AWS_S3_REGION_NAME',
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'AWS_LOCATION',
]

env_source = {}
for var in aws_vars:
    env_value = os.getenv(var)
    if env_value:
        if 'KEY' in var or 'SECRET' in var:
            display = env_value[:4] + '****' if len(env_value) > 4 else '****'
        else:
            display = env_value
        env_source[var] = f"Environment Variable: {display}"
        print(f"  ✓ {var}: Found in environment variable")
    else:
        env_source[var] = "Not in environment"
        print(f"  ✗ {var}: Not in environment variables")

print()
print("📋 Current Django Settings:")
print("-" * 60)

settings_values = {
    'USE_AWS': getattr(settings, 'USE_AWS', 'NOT SET'),
    'AWS_STORAGE_BUCKET_NAME': getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'NOT SET'),
    'AWS_S3_REGION_NAME': getattr(settings, 'AWS_S3_REGION_NAME', 'NOT SET'),
    'AWS_ACCESS_KEY_ID': getattr(settings, 'AWS_ACCESS_KEY_ID', 'NOT SET'),
    'AWS_SECRET_ACCESS_KEY': getattr(settings, 'AWS_SECRET_ACCESS_KEY', 'NOT SET'),
    'AWS_LOCATION': getattr(settings, 'AWS_LOCATION', 'NOT SET'),
    'MEDIA_URL': getattr(settings, 'MEDIA_URL', 'NOT SET'),
}

for key, value in settings_values.items():
    if key in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']:
        display = value[:4] + '****' if value and len(value) > 4 else value
    else:
        display = value
    status = "✓" if value and value != "NOT SET" and value != "" else "✗"
    print(f"{status} {key}: {display}")

print()
print("🔎 Source Analysis:")
print("-" * 60)

if settings_values['USE_AWS']:
    print("  ✓ USE_AWS is True - AWS is enabled")
    
    missing = []
    if not settings_values['AWS_STORAGE_BUCKET_NAME'] or settings_values['AWS_STORAGE_BUCKET_NAME'] == "":
        missing.append("AWS_STORAGE_BUCKET_NAME")
    if not settings_values['AWS_S3_REGION_NAME'] or settings_values['AWS_S3_REGION_NAME'] == "":
        missing.append("AWS_S3_REGION_NAME")
    if not settings_values['AWS_ACCESS_KEY_ID'] or settings_values['AWS_ACCESS_KEY_ID'] == "":
        missing.append("AWS_ACCESS_KEY_ID")
    if not settings_values['AWS_SECRET_ACCESS_KEY'] or settings_values['AWS_SECRET_ACCESS_KEY'] == "":
        missing.append("AWS_SECRET_ACCESS_KEY")
    
    if missing:
        print(f"\n  ❌ Missing required AWS settings: {', '.join(missing)}")
        print("\n  These are likely the problem!")
        print("\n  💡 Solution:")
        print("     Add these to your .env file:")
        print("     AWS_STORAGE_BUCKET_NAME=your-bucket-name")
        print("     AWS_S3_REGION_NAME=eu-west-1")
        print("     AWS_ACCESS_KEY_ID=your-access-key")
        print("     AWS_SECRET_ACCESS_KEY=your-secret-key")
    else:
        print("\n  ✓ All required AWS settings are configured")
        print("\n  💡 If images still don't work, check:")
        print("     - Bucket permissions")
        print("     - File path mismatch")
        print("     - IAM user permissions")
else:
    print("  ⚠️  USE_AWS is False - AWS is disabled")
    print("  Images are being stored locally, not in S3")

print()
print("📝 Checking .env file:")
print("-" * 60)
env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(env_file):
    print(f"  ✓ .env file exists at: {env_file}")
    with open(env_file, 'r') as f:
        content = f.read()
        aws_in_file = []
        for var in aws_vars:
            if var in content:
                aws_in_file.append(var)
        
        if aws_in_file:
            print(f"  ✓ Found AWS settings in .env: {', '.join(aws_in_file)}")
        else:
            print("  ✗ No AWS settings found in .env file")
            print("     This is likely the problem!")
else:
    print(f"  ✗ .env file not found at: {env_file}")

print()
print("=" * 60)
print("✅ Check Complete!")
print("=" * 60)





