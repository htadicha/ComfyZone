# 🔧 QUICK FIX: S3 Images Not Loading

## Your Issue
Images upload to S3 but return 403 Forbidden when viewing.

**Your image URL:** `https://hawashmart.s3.eu-west-1.amazonaws.com/media/products/16216048_rm405-c02a.jpg`

## ⚡ Fast Fix (5 minutes)

### 1. Go to AWS S3 Console
https://s3.console.aws.amazon.com/ → Select bucket: **hawashmart**

### 2. Disable Block Public ACLs
1. Click **Permissions** tab
2. Find **Block public access (bucket settings)**
3. Click **Edit**
4. **UNCHECK** these two boxes:
   - ☐ Block public access to buckets and objects granted through **new** ACLs
   - ☐ Block public access to buckets and objects granted through **any** ACLs
5. Click **Save changes** → Type `confirm` → **Confirm**

### 3. Add Bucket Policy
1. Still in **Permissions** tab
2. Scroll to **Bucket Policy**
3. Click **Edit**
4. Paste this (bucket name is already correct):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::hawashmart/*"
        }
    ]
}
```

5. Click **Save changes**

### 4. Fix Existing Images
**Option A (Easiest):** Re-upload images through Django admin  
**Option B:** Update ACL in S3 Console:
- Go to `media/products/` folder
- Select image → Actions → Change ACL → Check "Read" for Everyone → Save

### 5. Test
Open this URL in browser:  
`https://hawashmart.s3.eu-west-1.amazonaws.com/media/products/16216048_rm405-c02a.jpg`

✅ Should now load!

## Why This Happened
Your bucket has "Block Public ACLs" enabled, which overrides the `AWS_DEFAULT_ACL = 'public-read'` setting.

## After This Fix
- ✅ New uploads will work immediately
- ✅ Images will be publicly accessible
- ✅ No code changes needed




