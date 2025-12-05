# AWS Region Name Configuration

## Where It's Read From

The `AWS_S3_REGION_NAME` setting is configured in `furniture_store/settings.py` at **line 268**:

```python
AWS_S3_REGION_NAME = _normalize_region_name(config("AWS_S3_REGION_NAME", default=""))
```

## Configuration Sources (in order of priority)

The `config()` function (from `python-decouple`) reads from:

### 1. **Environment Variables** (Highest Priority)
   - System environment variables
   - Shell environment variables
   
### 2. **`.env` File** (Local Development)
   - Reads from `.env` file in project root
   - Format: `AWS_S3_REGION_NAME=eu-west-1`
   
### 3. **Heroku Config Vars** (Production)
   - Set via Heroku Dashboard or CLI
   - Command: `heroku config:set AWS_S3_REGION_NAME=eu-west-1 --app your-app-name`
   
### 4. **Default Value** (Fallback)
   - If not found anywhere, uses: `""` (empty string)

## How to Set It

### Local Development

Add to your `.env` file:
```env
AWS_S3_REGION_NAME=eu-west-1
```

### Production (Heroku)

Via CLI:
```bash
heroku config:set AWS_S3_REGION_NAME=eu-west-1 --app your-app-name
```

Via Heroku Dashboard:
1. Go to your app → Settings → Config Vars
2. Add: `AWS_S3_REGION_NAME` = `eu-west-1`

## Region Name Normalization

The setting uses a normalization function (lines 256-265) that:

- ✅ Accepts: `eu-west-1` → Returns: `eu-west-1`
- ✅ Accepts: `Europe (Ireland) eu-west-1` → Returns: `eu-west-1`
- ✅ Strips whitespace
- ✅ Extracts region code from formatted strings

This means you can set it as:
- `eu-west-1` (recommended)
- `Europe (Ireland) eu-west-1` (also works)

## Current Configuration

To check what value is currently set:

**Locally:**
```bash
python manage.py shell
```
Then:
```python
from django.conf import settings
print(f"AWS_S3_REGION_NAME: {settings.AWS_S3_REGION_NAME}")
```

**On Heroku:**
```bash
heroku config:get AWS_S3_REGION_NAME --app your-app-name
```

Or check all AWS settings:
```bash
heroku config --app your-app-name | grep AWS
```

## Usage

The region name is used to:
1. Construct the S3 bucket URL:
   ```python
   f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"
   ```

2. Connect to the correct AWS region for S3 operations

## Common Regions

- `us-east-1` - US East (N. Virginia)
- `us-west-1` - US West (N. California)
- `us-west-2` - US West (Oregon)
- `eu-west-1` - Europe (Ireland) ✅ Your current region
- `eu-central-1` - Europe (Frankfurt)
- `ap-southeast-1` - Asia Pacific (Singapore)

Make sure it matches your S3 bucket's actual region!




