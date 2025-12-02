# Media Files Not Loading in Production - Troubleshooting Guide

## The Problem

Product images work in local development but not in the deployed project. This happens because:

1. **Django only serves media files when `DEBUG=True`**
   - In `furniture_store/urls.py`, media files are only added to URL patterns when DEBUG is True
   - In production (`DEBUG=False`), Django won't serve these files

2. **Heroku's filesystem is ephemeral**
   - Files stored in the `media/` directory are deleted when the dyno restarts
   - Even if files were uploaded, they disappear after a restart

3. **Media files need cloud storage in production**
   - Unlike static files (CSS/JS) which can be served by WhiteNoise, media files (user uploads) require persistent storage
   - The recommended solution is AWS S3

## The Solution

Your project already has AWS S3 support built in! You just need to configure it.

### Step 1: Create an AWS S3 Bucket

1. Go to [AWS S3 Console](https://s3.console.aws.amazon.com/)
2. Create a new bucket (e.g., `your-app-name-media`)
3. Configure bucket settings:
   - **Block Public ACLs**: Unchecked (or configure bucket policy for public read)
   - **Bucket policy**: Add the following to allow public read access:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::your-bucket-name/*"
        }
    ]
}
```

### Step 2: Create IAM User for S3 Access

1. Go to [IAM Console](https://console.aws.amazon.com/iam/)
2. Create a new user (e.g., `django-s3-user`)
3. Attach a policy with these permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::your-bucket-name",
                "arn:aws:s3:::your-bucket-name/*"
            ]
        }
    ]
}
```

4. Create Access Key for this user and save the credentials

### Step 3: Set Heroku Config Vars

Set these environment variables on Heroku (via Dashboard or CLI):

```bash
# Via Heroku CLI
heroku config:set USE_AWS=True
heroku config:set AWS_STORAGE_BUCKET_NAME=your-bucket-name
heroku config:set AWS_S3_REGION_NAME=us-east-1  # or your region
heroku config:set AWS_ACCESS_KEY_ID=your-access-key-id
heroku config:set AWS_SECRET_ACCESS_KEY=your-secret-access-key
heroku config:set AWS_LOCATION=media
```

Or via Heroku Dashboard:
- Go to your app → Settings → Config Vars
- Add each variable above

### Step 4: Migrate Existing Media Files (Optional)

If you have existing product images, you'll need to:

1. **Upload existing local media files to S3:**
   - Use AWS Console to upload files from your local `media/products/` folder
   - Or use the AWS CLI: `aws s3 sync media/ s3://your-bucket-name/media/`

2. **Update database references:**
   - If file paths changed, you may need to update the database
   - The ImageField stores relative paths, so this should work automatically

### Step 5: Test

After setting up S3:

1. Restart your Heroku dyno: `heroku restart`
2. Upload a new product image through the admin panel
3. Check that the image URL points to S3 (should be `https://your-bucket.s3.region.amazonaws.com/media/...`)
4. Verify the image displays on your site

## Verification Checklist

- [ ] AWS S3 bucket created and configured
- [ ] IAM user created with proper permissions
- [ ] All Heroku config vars set correctly
- [ ] `USE_AWS=True` in production
- [ ] Bucket allows public read access (or configured CORS)
- [ ] Existing media files uploaded to S3 (if any)
- [ ] Test image upload works in production

## Common Issues

### Images still not loading after S3 setup

1. **Check bucket permissions**: Make sure the bucket allows public read access
2. **Verify config vars**: Run `heroku config` to ensure all AWS vars are set
3. **Check bucket region**: Ensure `AWS_S3_REGION_NAME` matches your bucket's region
4. **Verify bucket name**: Check for typos in `AWS_STORAGE_BUCKET_NAME`
5. **Restart dyno**: Changes require a restart: `heroku restart`

### CORS errors

If you see CORS errors when loading images:

1. Add CORS configuration to your S3 bucket:
```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "HEAD"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": []
    }
]
```

### 403 Forbidden errors

- Check IAM user permissions
- Verify bucket policy allows public read
- Check that the object exists in the bucket

## Alternative: Temporary Local Serving (NOT Recommended)

If you need a quick temporary solution for testing (NOT for production), you could modify `urls.py` to serve media files even when DEBUG=False. **However, this is not secure or persistent** - files will still be lost on Heroku restart.

```python
# Only use this for testing - NOT recommended for production
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... your existing patterns
]

# Serve media files in production (TEMPORARY - NOT RECOMMENDED)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

**Again, use AWS S3 for production - it's the proper solution!**

