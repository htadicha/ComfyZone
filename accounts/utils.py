from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import uuid
from .models import User


def send_verification_email(user):
    """Send email verification link to user."""
    token = uuid.uuid4()
    user.verification_token = token
    user.verification_token_expires = timezone.now() + timedelta(days=1)
    user.save()

    verification_url = f"{settings.SITE_URL}/accounts/verify-email/{token}/"
    
    subject = "Verify Your Email Address"
    message = f"""
    Thank you for registering with our furniture store!
    
    Please click the following link to verify your email address:
    {verification_url}
    
    This link will expire in 24 hours.
    
    If you did not create an account, please ignore this email.
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def verify_email_token(token):
    """Verify email token and activate user account."""
    try:
        user = User.objects.get(verification_token=token)
        if user.verification_token_expires and user.verification_token_expires > timezone.now():
            user.is_verified = True
            user.verification_token = None
            user.verification_token_expires = None
            user.save()
            return user
        return None
    except User.DoesNotExist:
        return None

