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
        Override _save to ensure file is uploaded and ACL is set to public-read.
        """
        import time
        
        # Get the location prefix
        location = self.location if hasattr(self, 'location') and self.location else getattr(settings, 'AWS_LOCATION', 'media')
        location = location.strip('/')
        
        # Ensure content is at the beginning
        if hasattr(content, 'seek'):
            content.seek(0)
        
        # Log at ERROR level to ensure it shows up
        logger.error(f"[STORAGE] Starting upload for file: {name}, location: {location}")
        logger.error(f"[STORAGE] Storage class: {self.__class__.__name__}, bucket: {getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'NOT SET')}")
        logger.error(f"[STORAGE] USE_AWS: {getattr(settings, 'USE_AWS', False)}")
        
        # Call parent _save to upload the file (this should use ACL from _get_write_parameters)
        try:
            saved_name = super()._save(name, content)
            logger.info(f"Parent _save completed, returned name: {saved_name}")
        except Exception as e:
            logger.error(f"Failed to upload file {name}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
        
        # Wait a moment for S3 eventual consistency
        time.sleep(0.5)
        
        # Verify file exists in S3 and set ACL
        bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', '')
        logger.error(
            "[STORAGE] ACL verify start",
            extra={
                "original_name": name,
                "saved_name": saved_name,
                "bucket": bucket_name,
                "location": location,
            },
        )
        
        if not bucket_name:
            logger.warning("AWS_STORAGE_BUCKET_NAME not set, skipping ACL verification")
            return saved_name
        
        # The saved_name from parent should already include location if configured correctly
        # But let's try multiple variations to be sure
        possible_keys = [
            saved_name,  # As returned by parent
            f"{location}/{saved_name}" if not saved_name.startswith(location) else saved_name,
            saved_name.lstrip('/'),
            f"/{saved_name}",
        ]
        
        # Remove duplicates
        seen = set()
        unique_keys = []
        for key in possible_keys:
            if key and key not in seen:
                seen.add(key)
                unique_keys.append(key)
        
        logger.error(
            "[STORAGE] Checking uploaded file in S3",
            extra={
                "bucket": bucket_name,
                "location": location,
                "original_name": name,
                "saved_name": saved_name,
                "possible_keys": possible_keys,
                "unique_keys": unique_keys,
            },
        )
        
        # Initialize S3 client
        try:
            s3_client = boto3.client(
                's3',
                region_name=getattr(settings, 'AWS_S3_REGION_NAME', ''),
                aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', ''),
                aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', '')
            )
            
            # Try to find the file and set ACL
            file_found = False
            actual_key = None
            
            for key in unique_keys:
                try:
                    # Check if file exists
                    logger.info(f"[STORAGE] head_object check -> bucket={bucket_name}, key={key}")
                    s3_client.head_object(Bucket=bucket_name, Key=key)
                    file_found = True
                    actual_key = key
                    logger.info(f"✓ File found in S3 at key: {key}")
                    break
                except ClientError as e:
                    if e.response['Error']['Code'] == '404':
                        logger.debug(f"File not found at key: {key}")
                        continue
                    else:
                        logger.warning(f"Error checking key {key}: {e}")
                        continue
            
            if not file_found:
                logger.error(f"✗ File not found in S3 after upload! Tried keys: {unique_keys}")
                logger.error(f"  Original name: {name}, Saved name: {saved_name}")
                # Don't fail - let the signal handler try later
                return saved_name
            
            # File exists, now set ACL to public-read (backup in case _get_write_parameters didn't work)
            try:
                logger.info(f"[STORAGE] put_object_acl public-read -> bucket={bucket_name}, key={actual_key}")
                s3_client.put_object_acl(
                    Bucket=bucket_name,
                    Key=actual_key,
                    ACL='public-read'
                )
                logger.info(f"✓ Set ACL to public-read for {actual_key}")
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', '')
                if 'BlockPublicAccess' in str(e) or error_code == 'AccessDenied':
                    logger.error(f"✗ Cannot set ACL for {actual_key}: Block Public Access may be enabled or IAM permissions missing")
                else:
                    logger.warning(f"Failed to set ACL to public-read for {actual_key}: {e}")
        except Exception as e:
            # Log error but don't fail the upload
            logger.error(f"Exception while verifying/setting ACL: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        return saved_name
