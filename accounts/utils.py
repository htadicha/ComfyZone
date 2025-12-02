import logging
import uuid
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import User

logger = logging.getLogger(__name__)


def _issue_verification_token(user, validity_hours: int = 24):
    """Assign a fresh verification token and expiry to the user."""
    token = uuid.uuid4()
    user.verification_token = token
    user.verification_token_expires = timezone.now() + timedelta(hours=validity_hours)
    user.save(update_fields=["verification_token", "verification_token_expires"])
    return token


def send_verification_email(user, *, regenerate_token: bool = True):
    """Send email verification link to user."""
    if regenerate_token or not user.verification_token or not user.verification_token_expires:
        token = _issue_verification_token(user)
    else:
        # Ensure existing token is still valid; otherwise refresh it.
        if user.verification_token_expires <= timezone.now():
            token = _issue_verification_token(user)
        else:
            token = user.verification_token

    verification_url = f"{settings.SITE_URL}/accounts/verify-email/{token}/"

    subject = "Verify Your Email Address"
    message = (
        "Thank you for registering with our furniture store!\n\n"
        "Please click the following link to verify your email address:\n"
        f"{verification_url}\n\n"
        "This link will expire in 24 hours.\n\n"
        "If you did not create an account, please ignore this email."
    )

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
    except Exception:
        logger.exception("Failed to send verification email to %s", user.email)
        raise


def verify_email_token(token):
    """Verify email token and activate user account."""
    if not token:
        return None

    try:
        user = User.objects.get(verification_token=token)
    except User.DoesNotExist:
        return None

    if user.verification_token_expires and user.verification_token_expires > timezone.now():
        user.is_verified = True
        user.is_active = True
        user.verification_token = uuid.uuid4()
        user.verification_token_expires = None
        user.save(update_fields=["is_verified", "is_active", "verification_token", "verification_token_expires"])
        return user

    return None
