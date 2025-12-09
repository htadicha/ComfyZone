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
        # Get the location prefix
        location = self.location if hasattr(self, 'location') and self.location else getattr(settings, 'AWS_LOCATION', 'media')
        location = location.strip('/')
        
        # Normalize the name first
        cleaned_name = self._clean_name(name)
        normalized_name = self._normalize_name(cleaned_name)
        
        # Construct the full S3 key with location
        if normalized_name.startswith(location + '/'):
            s3_key = normalized_name
        elif normalized_name.startswith('/'):
            s3_key = f"{location}{normalized_name}"
        else:
            s3_key = f"{location}/{normalized_name}"
        
        # Call parent _save to upload the file (this should use ACL from _get_write_parameters)
        saved_name = super()._save(name, content)
        
        # Explicitly set ACL to public-read using boto3 (backup mechanism)
        # Use the s3_key we constructed, not the returned name
        try:
            s3_client = boto3.client(
                's3',
                region_name=getattr(settings, 'AWS_S3_REGION_NAME', ''),
                aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', ''),
                aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', '')
            )
            
            bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', '')
            
            # Set ACL to public-read
            s3_client.put_object_acl(
                Bucket=bucket_name,
                Key=s3_key,
                ACL='public-read'
            )
            logger.info(f"Set ACL to public-read for {s3_key}")
        except Exception as e:
            # Log error but don't fail the upload
            # The post_save signal will also try to set ACL
            logger.warning(f"Failed to set ACL to public-read for {s3_key}: {e}")
            # Try with the returned name as fallback
            try:
                fallback_key = f"{location}/{saved_name}" if not saved_name.startswith(location) else saved_name
                s3_client.put_object_acl(
                    Bucket=bucket_name,
                    Key=fallback_key,
                    ACL='public-read'
                )
                logger.info(f"Set ACL to public-read for {fallback_key} (fallback)")
            except:
                pass
        
        return saved_name

