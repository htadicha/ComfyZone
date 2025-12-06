# AWS S3 Configuration Verification

## Configuration Analysis

I've reviewed your AWS S3 configuration in `furniture_store/settings.py`. Here's what I found:

### ✅ What's Configured Correctly

1. **Package Installation**: `django-storages[boto3]>=1.14.3` is in requirements.txt ✓
2. **Storage Backend**: `DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"` ✓
3. **Media URL**: Configured to use S3 domain when `USE_AWS=True` ✓
4. **Region Normalization**: Handles different region name formats ✓
5. **Custom Domain Support**: Can use custom S3 domain ✓
6. **File Overwrite Protection**: `AWS_S3_FILE_OVERWRITE = False` ✓
7. **Cache Control**: Set to 86400 seconds (24 hours) ✓

### ⚠️ Potential Issue Found

**`AWS_DEFAULT_ACL = None`** - This setting may prevent public access to uploaded images!

When `AWS_DEFAULT_ACL = None`, uploaded objects won't have any ACL set, which typically means they won't be publicly accessible. For product images that need to be visible to website visitors, you have two options:

#### Option 1: Set Public Read ACL (Recommended for public images)
```python
AWS_DEFAULT_ACL = 'public-read'
```

#### Option 2: Keep ACL as None and use Bucket Policy (More secure)
Keep `AWS_DEFAULT_ACL = None` but ensure your S3 bucket has a bucket policy that allows public read access.

## Required Heroku Config Vars

Verify these are set on Heroku:

- [ ] `USE_AWS=True`
- [ ] `AWS_STORAGE_BUCKET_NAME` (your bucket name)
- [ ] `AWS_S3_REGION_NAME` (e.g., `us-east-1`, `eu-west-1`)
- [ ] `AWS_ACCESS_KEY_ID`
- [ ] `AWS_SECRET_ACCESS_KEY`
- [ ] `AWS_LOCATION` (defaults to `media` if not set)

### Optional Config Vars

- `AWS_S3_CUSTOM_DOMAIN` - Only if using CloudFront or custom domain
- `AWS_S3_SIGNATURE_VERSION` - Defaults to `s3v4` (correct)

## Verification Checklist

### 1. Check Heroku Config Vars

```bash
heroku config --app your-app-name
```

Look for all AWS-related variables listed above.

### 2. Test S3 Connection

Run this in Heroku shell to test:

```bash
heroku run python manage.py shell --app your-app-name
```

Then in the shell:

```python
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

# Check if AWS is enabled
print(f"USE_AWS: {settings.USE_AWS}")
print(f"Bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
print(f"Region: {settings.AWS_S3_REGION_NAME}")
print(f"Media URL: {settings.MEDIA_URL}")

# Test storage connection
storage = S3Boto3Storage()
try:
    storage.listdir('')
    print("✅ S3 connection successful!")
except Exception as e:
    print(f"❌ S3 connection failed: {e}")
```

### 3. Check Bucket Permissions

In AWS S3 Console:
- [ ] Bucket exists
- [ ] Bucket policy allows public read (if using public images)
- [ ] OR objects have `public-read` ACL set

### 4. Check IAM Permissions

The IAM user should have:
- [ ] `s3:PutObject`
- [ ] `s3:GetObject`
- [ ] `s3:DeleteObject`
- [ ] `s3:ListBucket`

### 5. Test Image Upload

1. Go to your admin panel on Heroku
2. Upload a product image
3. Check the image URL - it should start with `https://your-bucket.s3.region.amazonaws.com/`
4. Open the URL directly in a browser to verify it's accessible

### 6. Common Issues to Check

#### Images upload but return 403 Forbidden
- **Cause**: Missing public read permissions
- **Fix**: Set `AWS_DEFAULT_ACL = 'public-read'` OR configure bucket policy

#### Images upload but URL is wrong
- **Cause**: Incorrect `AWS_S3_CUSTOM_DOMAIN` or region
- **Fix**: Verify bucket name and region match AWS console

#### Images don't upload at all
- **Cause**: Wrong IAM credentials or permissions
- **Fix**: Verify `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are correct

#### Old images from local still show broken
- **Cause**: Database still references local paths
- **Fix**: Re-upload images OR migrate existing files to S3 and update database

## Recommended Fix

If images aren't accessible, I recommend updating the ACL setting. Here's what needs to change:

**File**: `furniture_store/settings.py`  
**Line**: 273  
**Current**: `AWS_DEFAULT_ACL = None`  
**Recommended**: `AWS_DEFAULT_ACL = 'public-read'`

This will make uploaded images publicly accessible, which is typically what you want for product images on an e-commerce site.





