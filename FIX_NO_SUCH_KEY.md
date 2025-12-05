# 🔍 Fix: NoSuchKey Error - File Not Found in S3

## Your Error
```
<Code>NoSuchKey</Code>
<Message>The specified key does not exist.</Message>
<Key>media/products/16216048_rm405-c02a.jpg</Key>
```

This means: **The file doesn't exist at that path in S3**

## Possible Causes

1. ❌ **File was never uploaded** - Upload failed silently
2. ❌ **File uploaded to wrong location** - Path mismatch
3. ❌ **File uploaded with different name** - Name changed during upload
4. ❌ **AWS_LOCATION mismatch** - Files stored in different prefix

## Quick Diagnosis

### Step 1: Check if File Exists in S3

**Option A: AWS Console (Easiest)**
1. Go to https://s3.console.aws.amazon.com/
2. Open bucket: `hawashmart`
3. Navigate to `media/products/` folder
4. Look for file: `16216048_rm405-c02a.jpg`
   - ✅ **If found:** The path in URL is wrong
   - ❌ **If not found:** File was never uploaded

**Option B: Run Diagnostic Script**
```bash
python check_s3_file_location.py
```
This will show:
- Where files actually are in S3
- What URLs Django thinks they have
- List all files in your S3 bucket

### Step 2: Check Database vs S3

Run this in Django shell:
```bash
python manage.py shell
```

Then:
```python
from store.models import ProductImage

# Find the image
img = ProductImage.objects.filter(image__contains='16216048_rm405-c02a.jpg').first()
if img:
    print(f"Database path: {img.image.name}")
    print(f"Full URL: {img.image.url}")
    print(f"Storage path: {img.image.storage.location}/{img.image.name}")
else:
    print("Image not found in database!")
```

### Step 3: Check Actual S3 Contents

In Django shell:
```python
from storages.backends.s3boto3 import S3Boto3Storage

storage = S3Boto3Storage()
files, dirs = storage.listdir('media/products/')
print(f"Files in media/products/: {files[:20]}")  # First 20 files
```

## Common Fixes

### Fix 1: File Never Uploaded → Re-upload

**If file doesn't exist in S3:**
1. Go to Django admin
2. Edit the product
3. Delete the broken image
4. Upload the image again
5. Check if upload succeeds (no errors)
6. Verify new URL works

### Fix 2: Path Mismatch → Check AWS_LOCATION

Check your Heroku config:
```bash
heroku config --app your-app-name | grep AWS_LOCATION
```

Should be: `AWS_LOCATION=media` (or empty, defaults to `media`)

If different, update it:
```bash
heroku config:set AWS_LOCATION=media --app your-app-name
```

### Fix 3: Upload Failed → Check IAM Permissions

The upload might be failing silently. Check Heroku logs:
```bash
heroku logs --tail --app your-app-name
```

Look for errors when uploading images.

Verify IAM permissions include:
- `s3:PutObject`
- `s3:PutObjectAcl` (for public-read ACL)

### Fix 4: Wrong Bucket or Region

Verify settings match your S3 bucket:
```bash
heroku config --app your-app-name | grep AWS
```

Check:
- `AWS_STORAGE_BUCKET_NAME` = `hawashmart` ✅
- `AWS_S3_REGION_NAME` = `eu-west-1` ✅

## Immediate Action Steps

1. ✅ **Check AWS Console** - Does the file exist?
2. ✅ **Run diagnostic script** - `python check_s3_file_location.py`
3. ✅ **Check upload logs** - Any errors during upload?
4. ✅ **Re-upload image** - Try uploading again
5. ✅ **Check IAM permissions** - Can Django write to S3?

## Next Steps

After running the diagnostic script, you'll know:
- ✅ Where files actually are
- ✅ What paths Django is using
- ✅ If uploads are working

Then we can fix the exact issue!




