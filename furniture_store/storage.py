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
    """Media storage backend that enforces public-read ACL on S3."""

    default_acl = "public-read"
    file_overwrite = False

    def __init__(self, *args, **kwargs):
        if "location" not in kwargs:
            kwargs["location"] = getattr(settings, "AWS_LOCATION", "media")
        super().__init__(*args, **kwargs)
        if not self.location:
            self.location = getattr(settings, "AWS_LOCATION", "media")
    
    def _get_write_parameters(self, name, content):
        """Ensure uploads request public-read ACL."""
        params = super()._get_write_parameters(name, content)
        params["ACL"] = "public-read"
        return params
    
    def _save(self, name, content):
        """Upload file then verify S3 ACL is public-read."""
        import time
        
        location = self.location if hasattr(self, 'location') and self.location else getattr(settings, 'AWS_LOCATION', 'media')
        location = location.strip('/')
        
        if hasattr(content, 'seek'):
            content.seek(0)
        
        logger.error(f"[STORAGE] Starting upload for file: {name}, location: {location}")
        logger.error(f"[STORAGE] Storage class: {self.__class__.__name__}, bucket: {getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'NOT SET')}")
        logger.error(f"[STORAGE] USE_AWS: {getattr(settings, 'USE_AWS', False)}")
        
        try:
            saved_name = super()._save(name, content)
            logger.info(f"Parent _save completed, returned name: {saved_name}")
        except Exception as e:
            logger.error(f"Failed to upload file {name}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
        
        time.sleep(0.5)
        
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
        
        possible_keys = [
            saved_name,
            f"{location}/{saved_name}" if not saved_name.startswith(location) else saved_name,
            saved_name.lstrip('/'),
            f"/{saved_name}",
        ]
        
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
        
        try:
            s3_client = boto3.client(
                's3',
                region_name=getattr(settings, 'AWS_S3_REGION_NAME', ''),
                aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', ''),
                aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', '')
            )
            
            file_found = False
            actual_key = None
            
            for key in unique_keys:
                try:
                    logger.info(f"[STORAGE] head_object check -> bucket={bucket_name}, key={key}")
                    s3_client.head_object(Bucket=bucket_name, Key=key)
                    file_found = True
                    actual_key = key
                    logger.info(f"File found in S3 at key: {key}")
                    break
                except ClientError as e:
                    if e.response['Error']['Code'] == '404':
                        logger.debug(f"File not found at key: {key}")
                        continue
                    else:
                        logger.warning(f"Error checking key {key}: {e}")
                        continue
            
            if not file_found:
                logger.error(f"File not found in S3 after upload. Tried keys: {unique_keys}")
                logger.error(f"Original name: {name}, Saved name: {saved_name}")
                return saved_name
            
            try:
                logger.info(f"[STORAGE] put_object_acl public-read -> bucket={bucket_name}, key={actual_key}")
                s3_client.put_object_acl(
                    Bucket=bucket_name,
                    Key=actual_key,
                    ACL='public-read'
                )
                logger.info(f"Set ACL to public-read for {actual_key}")
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', '')
                if 'BlockPublicAccess' in str(e) or error_code == 'AccessDenied':
                    logger.error(f"Cannot set ACL for {actual_key}: Block Public Access may be enabled or IAM permissions missing")
                else:
                    logger.warning(f"Failed to set ACL to public-read for {actual_key}: {e}")
        except Exception as e:
            logger.error(f"Exception while verifying/setting ACL: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        return saved_name
