# S3 Public Access Checklist

If product images are still broken even after the MediaStorage fix, check these S3 bucket settings:

## 1. Check S3 Bucket "Block Public Access" Settings

**This is the most common issue!**

1. Go to AWS S3 Console
2. Select your bucket (`comfyzone` or `hawashmart`)
3. Go to **Permissions** tab
4. Scroll down to **Block public access (bucket settings)**
5. Click **Edit**
6. **UNCHECK** all four options:
   - ☐ Block all public access
   - ☐ Block public access to buckets and objects granted through new access control lists (ACLs)
   - ☐ Block public access to buckets and objects granted through any access control lists (ACLs)
   - ☐ Block public access to buckets and objects granted through new public bucket or access point policies
7. Click **Save changes**

**Note:** AWS will warn you about making the bucket public. This is expected for product images that need to be publicly accessible.

## 2. Check Bucket Policy

1. In the same **Permissions** tab
2. Scroll to **Bucket policy**
3. Ensure you have a policy that allows public read access:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
    }
  ]
}
```

Replace `YOUR-BUCKET-NAME` with your actual bucket name (e.g., `comfyzone` or `hawashmart`).

## 3. Verify Object ACL

1. In S3 Console, navigate to a broken product image
2. Click on the image file
3. Go to **Permissions** tab
4. Under **Access control list (ACL)**, check if it shows:
   - **Public access**: ✅ Objects can be public
   - **Everyone (public access)**: ✅ Read

If not, the ACL fix script should have fixed this, but you can manually set it:
- Click **Edit**
- Under **Public access**, check **Read** for **Everyone**
- Save

## 4. Test the Configuration

Run the test script to verify ACL is being set correctly:

```bash
python test_storage_acl.py
```

Or on Heroku:
```bash
heroku run python test_storage_acl.py
```

## 5. Fix Existing Images

After verifying bucket settings, run the ACL fix script:

```bash
python fix_s3_acl.py
```

Or on Heroku:
```bash
heroku run python fix_s3_acl.py
```

## Common Issues

### Issue: "Access Denied" when accessing image URL
**Solution:** Check #1 above - Block Public Access is likely enabled

### Issue: Images work in admin but not on website
**Solution:** Check #2 above - Bucket policy might be missing

### Issue: Old images broken but new ones work
**Solution:** Run the `fix_s3_acl.py` script to fix existing images

### Issue: All images broken including new uploads
**Solution:** 
1. Check #1 - Block Public Access settings
2. Verify `AWS_DEFAULT_ACL = 'public-read'` in settings
3. Run `test_storage_acl.py` to verify storage class is working

