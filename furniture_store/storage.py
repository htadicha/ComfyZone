"""
Custom storage backends for AWS S3.
"""
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)


class MediaStorage(S3Boto3Storage):
    """
    Custom storage class for media files (product images, etc.)
    Sets ACL to 'public-read' so files are publicly accessible.
    
    The location (prefix) is controlled by AWS_LOCATION in settings.
    """
    default_acl = 'public-read'
    file_overwrite = False
    
    def __init__(self, *args, **kwargs):
        # Set location before calling super() so it's available
        if 'location' not in kwargs:
            kwargs['location'] = getattr(settings, 'AWS_LOCATION', 'media')
        super().__init__(*args, **kwargs)
        # Ensure location is set from settings
        if not self.location:
            self.location = getattr(settings, 'AWS_LOCATION', 'media')
    
    def _get_write_parameters(self, content):
        """
        Override to ensure ACL is always set to public-read.
        """
        params = super()._get_write_parameters(content)
        # Force ACL to public-read
        params['ACL'] = 'public-read'
        return params
    
    def _save(self, name, content):
        """
        Override _save to ensure ACL is set to public-read after upload.
        Uses parent's _save but then explicitly sets ACL as backup.
        """
        try:
            # Call parent _save to upload the file (this should use ACL from _get_write_parameters)
            name = super()._save(name, content)
            logger.info(f"File uploaded successfully via parent _save: {name}")
        except Exception as e:
            logger.error(f"Failed to upload file {name}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
        
        # Verify file exists in S3 before trying to set ACL
        # Get the actual S3 key that was used
        bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', '')
        
        # The name returned from super()._save() is the relative path
        # We need to construct the full S3 key with location
        location = self.location if hasattr(self, 'location') and self.location else getattr(settings, 'AWS_LOCATION', 'media').strip('/')
        
        # Construct S3 key
        if name.startswith(location + '/'):
            s3_key = name
        elif name.startswith('/'):
            s3_key = f"{location}{name}"
        else:
            s3_key = f"{location}/{name}"
        
        # Verify file exists before setting ACL
        try:
            s3_client = boto3.client(
                's3',
                region_name=getattr(settings, 'AWS_S3_REGION_NAME', ''),
                aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', ''),
                aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', '')
            )
            
            # Check if file exists
            try:
                s3_client.head_object(Bucket=bucket_name, Key=s3_key)
                logger.info(f"Verified file exists in S3: {s3_key}")
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    logger.error(f"File was not uploaded to S3! Key: {s3_key}")
                    # Try alternative key formats
                    alt_keys = [
                        name,  # Without location
                        f"/{name}",  # With leading slash
                        f"{location}{name}",  # Location without slash
                    ]
                    for alt_key in alt_keys:
                        try:
                            s3_client.head_object(Bucket=bucket_name, Key=alt_key)
                            logger.warning(f"File found at alternative key: {alt_key} (expected: {s3_key})")
                            s3_key = alt_key
                            break
                        except ClientError:
                            continue
                    else:
                        logger.error(f"File not found at any expected location. Upload may have failed.")
                        return name  # Return anyway, signal will try later
            
            # File exists, now set ACL to public-read
            s3_client.put_object_acl(
                Bucket=bucket_name,
                Key=s3_key,
                ACL='public-read'
            )
            logger.info(f"Set ACL to public-read for {s3_key}")
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if 'BlockPublicAccess' in str(e) or error_code == 'AccessDenied':
                logger.error(f"Cannot set ACL for {s3_key}: Block Public Access may be enabled or IAM permissions missing")
            else:
                logger.warning(f"Failed to set ACL to public-read for {s3_key}: {e}")
        except Exception as e:
            # Log error but don't fail the upload
            logger.warning(f"Failed to set ACL to public-read for {s3_key}: {e}")
        
        return name

