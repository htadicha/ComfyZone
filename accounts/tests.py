from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from allauth.account.models import EmailAddress, EmailConfirmationHMAC

from .models import Profile, User


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class RegistrationFlowTests(TestCase):
    def test_register_creates_inactive_user_and_sends_email(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "email": "jane@example.com",
                "first_name": "Jane",
                "last_name": "Doe",
                "password1": "complex-password-123",
                "password2": "complex-password-123",
            },
            follow=False,
        )

        self.assertRedirects(response, reverse("accounts:login"))
        user = User.objects.get(email="jane@example.com")
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_verified)
        self.assertTrue(Profile.objects.filter(user=user).exists())

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("/accounts/confirm-email/", mail.outbox[0].body)
        self.assertTrue(
            EmailAddress.objects.filter(user=user, email=user.email, verified=False, primary=True).exists()
        )

    def test_verify_email_activates_user(self):
        user = User.objects.create_user(
            email="mark@example.com",
            password="password123",
            first_name="Mark",
            last_name="Twain",
        )
        user.is_active = False
        user.is_verified = False
        user.save()

        email_address = EmailAddress.objects.create(user=user, email=user.email, primary=True, verified=False)
        confirmation = EmailConfirmationHMAC(email_address)

        response = self.client.get(reverse("account_confirm_email", args=[confirmation.key]), follow=True)

        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_verified)
        email_address.refresh_from_db()
        self.assertTrue(email_address.verified)
        self.assertEqual(response.status_code, 200)

    def test_resend_verification_creates_new_token_and_email(self):
        user = User.objects.create_user(
            email="mike@example.com",
            password="password123",
            first_name="Mike",
            last_name="Jones",
        )
        user.is_active = False
        user.is_verified = False
        user.save()

        response = self.client.post(
            reverse("accounts:resend_verification"),
            {"email": user.email},
            follow=False,
        )
        self.assertRedirects(response, reverse("accounts:login"))

        user.refresh_from_db()
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("/accounts/confirm-email/", mail.outbox[0].body)
        self.assertTrue(
            EmailAddress.objects.filter(user=user, email=user.email, verified=False, primary=True).exists()
        )
