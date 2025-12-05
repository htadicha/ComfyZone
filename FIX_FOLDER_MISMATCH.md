# 🔧 Fix: Folder Name Mismatch - photos vs media

## Problem Found! ✅

Your S3 folder is named: **`photos/products/`**  
But Django is looking for: **`media/products/`**

## Quick Fix

Update your Heroku config variable `AWS_LOCATION` to match your actual folder name:

```bash
heroku config:set AWS_LOCATION=photos --app comfyzone-907dbe348f5b
```

## Why This Happens

Django uses the `AWS_LOCATION` setting as the root folder prefix in S3. Your configuration currently defaults to `media`, but your S3 bucket uses `photos`.

**Current configuration:**
- `AWS_LOCATION` = `media` (default)
- Django looks for: `media/products/your-image.jpg`
- Actual S3 location: `photos/products/your-image.jpg` ❌

**After fix:**
- `AWS_LOCATION` = `photos`
- Django will look for: `photos/products/your-image.jpg` ✅
- Actual S3 location: `photos/products/your-image.jpg` ✅

## Steps to Fix

### Step 1: Update Heroku Config Var

```bash
heroku config:set AWS_LOCATION=photos --app comfyzone-907dbe348f5b
```

### Step 2: Restart the App

```bash
heroku restart --app comfyzone-907dbe348f5b
```

### Step 3: Verify

After restarting, check the MEDIA_URL:

```bash
heroku run python manage.py shell --app comfyzone-907dbe348f5b
```

Then in the shell:
```python
from django.conf import settings
print(f"AWS_LOCATION: {settings.AWS_LOCATION}")
print(f"MEDIA_URL: {settings.MEDIA_URL}")
```

The MEDIA_URL should now be:
```
https://hawashmart.s3.eu-west-1.amazonaws.com/photos/
```

### Step 4: Test

Try accessing your image:
```
https://hawashmart.s3.eu-west-1.amazonaws.com/photos/products/16216048_rm405-c02a.jpg
```

## Alternative: Rename Your S3 Folder

If you prefer to keep `media` as the folder name:

1. In AWS S3 Console, rename folder `photos` to `media`
2. Keep `AWS_LOCATION=media` (or don't set it, uses default)

But updating the config var is easier! ✅

## After Fix

✅ New uploads will go to: `photos/products/`  
✅ URLs will point to: `https://hawashmart.s3.eu-west-1.amazonaws.com/photos/products/...`  
✅ Existing images will be accessible at the correct path




