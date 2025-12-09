import logging

from allauth.account.models import EmailAddress, EmailConfirmation, EmailConfirmationHMAC
from allauth.account.utils import send_email_confirmation

logger = logging.getLogger(__name__)


def _ensure_primary_email_address(user):
    """
    Make sure the user has a primary EmailAddress record for allauth.
    This keeps email verification and login flows in sync with allauth.
    """
    email_address, _ = EmailAddress.objects.get_or_create(
        user=user,
        email=user.email,
        defaults={"primary": True, "verified": False},
    )

    if not email_address.primary:
        email_address.set_as_primary()

    return email_address


def send_verification_email(user, *, request=None, signup: bool = True):
    """
    Issue an allauth email confirmation for the given user.

    The `signup` flag is passed through to allauth so that the correct
    email template is used for first-time confirmations vs. manual resends.
    """
    email_address = _ensure_primary_email_address(user)

    if email_address.verified:
        logger.info("User %s already verified; skipping confirmation email.", user.email)
        return email_address

    send_email_confirmation(request, user, signup=signup)
    return email_address


def verify_email_token(key, request=None):
    """
    Confirm an allauth email confirmation key and return the user, or None.

    This provides a bridge for the legacy verify-email URL to use the
    allauth confirmation model, so existing links continue to function.
    """
    if not key:
        return None

    try:
        confirmation = EmailConfirmationHMAC.from_key(key)
    except Exception:
        confirmation = None

    if confirmation:
        confirmation.confirm(request)
        return confirmation.email_address.user

    confirmation = EmailConfirmation.objects.filter(key=key).first()
    if confirmation:
        confirmation.confirm(request)
        return confirmation.email_address.user

    return None
