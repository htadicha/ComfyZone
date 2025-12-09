#!/usr/bin/env python
"""
Script to check S3 bucket policy and create one if needed.
This is an alternative if you cannot disable "Block Public Access".
"""
import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'furniture_store.settings')
django.setup()

from django.conf import settings
import boto3
from botocore.exceptions import ClientError

print("=" * 70)
print("S3 Bucket Policy Checker and Creator")
print("=" * 70)
print()

if not getattr(settings, 'USE_AWS', False):
    print("❌ AWS is not enabled!")
    sys.exit(1)

bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', '')
region_name = getattr(settings, 'AWS_S3_REGION_NAME', '')
aws_access_key_id = getattr(settings, 'AWS_ACCESS_KEY_ID', '')
aws_secret_access_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', '')

if not all([bucket_name, region_name, aws_access_key_id, aws_secret_access_key]):
    print("❌ Missing required AWS configuration!")
    sys.exit(1)

s3_client = boto3.client(
    's3',
    region_name=region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

print(f"Bucket: {bucket_name}")
print(f"Region: {region_name}")
print()

print("1️⃣  Checking Current Bucket Policy")
print("-" * 70)
try:
    policy_response = s3_client.get_bucket_policy(Bucket=bucket_name)
    current_policy = json.loads(policy_response['Policy'])
    print("   ✅ Bucket policy exists")
    print(f"   Policy JSON:")
    print(json.dumps(current_policy, indent=2))
    
    statements = current_policy.get('Statement', [])
    public_read_allowed = False
    for statement in statements:
        if (statement.get('Effect') == 'Allow' and
            statement.get('Principal') == '*' and
            's3:GetObject' in statement.get('Action', [])):
            public_read_allowed = True
            break
    
    if public_read_allowed:
        print("\n   ✅ Policy allows public read access")
    else:
        print("\n   ⚠️  Policy does NOT allow public read access")
        print("   → You need to add a statement to allow public read")
        
except ClientError as e:
    if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
        print("   ⚠️  No bucket policy exists")
        print("   → A bucket policy is needed for public access")
    else:
        print(f"   ❌ Error checking policy: {e}")
        sys.exit(1)

print()

print("2️⃣  Block Public Access Settings")
print("-" * 70)
print("   ⚠️  This must be checked manually in AWS Console")
print()
print("   IMPORTANT: If 'Block Public Access' is ENABLED, you have two options:")
print()
print("   Option 1 (RECOMMENDED): Disable Block Public Access")
print("   - Go to S3 Console → Your Bucket → Permissions")
print("   - Click 'Edit' on 'Block public access (bucket settings)'")
print("   - UNCHECK all four options")
print("   - Save and confirm")
print()
print("   Option 2: Use Bucket Policy (if you can't disable Block Public Access)")
print("   - See the policy below")
print("   - Note: This may not work if Block Public Access blocks ACLs")
print()

print("3️⃣  Recommended Bucket Policy")
print("-" * 70)
recommended_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{bucket_name}/*"
        }
    ]
}

print("   Copy this policy to your S3 bucket:")
print()
print(json.dumps(recommended_policy, indent=2))
print()

print("4️⃣  Apply Bucket Policy?")
print("-" * 70)
print("   ⚠️  WARNING: This will REPLACE your existing bucket policy!")
print()
response = input("   Do you want to apply this policy? (yes/no): ").strip().lower()

if response == 'yes':
    try:
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(recommended_policy)
        )
        print("   ✅ Bucket policy applied successfully!")
        print()
        print("   ⚠️  IMPORTANT: You still need to disable 'Block Public Access'")
        print("   → Go to S3 Console → Your Bucket → Permissions")
        print("   → Edit 'Block public access' settings and uncheck all options")
    except ClientError as e:
        print(f"   ❌ Error applying policy: {e}")
        if 'AccessDenied' in str(e):
            print("   → Your IAM user needs 's3:PutBucketPolicy' permission")
else:
    print("   Policy not applied. Apply it manually in AWS Console if needed.")

print()
print("=" * 70)
print("📋 NEXT STEPS")
print("=" * 70)
print()
print("1. Disable 'Block Public Access' in S3 Console (RECOMMENDED)")
print("   → This is the proper solution for public product images")
print()
print("2. If you can't disable it, apply the bucket policy above")
print("   → But this may still not work if ACLs are blocked")
print()
print("3. After fixing, run: python fix_s3_acl.py")
print("   → This will set ACL on existing images")
print()
print("4. Test by uploading a new product image")
print()
print("=" * 70)

