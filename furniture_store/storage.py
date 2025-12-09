"""
Custom storage backends for AWS S3.
"""
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
import boto3
from botocore.exceptions import ClientError


class MediaStorage(S3Boto3Storage):
    """
    Custom storage class for media files (product images, etc.)
    Sets ACL to 'public-read' so files are publicly accessible.
    
    The location (prefix) is controlled by AWS_LOCATION in settings.
    """
    default_acl = 'public-read'
    file_overwrite = False
    
    def _save(self, name, content):
        """
        Override _save to ensure ACL is set to public-read after upload.
        """
        # Call parent _save to upload the file
        name = super()._save(name, content)
        
        # Get the full S3 key - django-storages already includes location in the name
        # But we need to ensure we have the correct key
        aws_location = getattr(settings, 'AWS_LOCATION', 'media')
        
        # The name returned from super()._save() should already include location
        # But let's construct it properly
        if name.startswith(aws_location + '/'):
            s3_key = name
        elif name.startswith('/'):
            s3_key = f"{aws_location}{name}"
        else:
            s3_key = f"{aws_location}/{name}"
        
        # Explicitly set ACL to public-read using boto3
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
        except Exception as e:
            # Log error but don't fail the upload
            # The post_save signal will also try to set ACL
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to set ACL to public-read for {s3_key}: {e}")
        
        return name

