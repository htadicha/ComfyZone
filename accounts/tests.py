import uuid
from datetime import timedelta

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

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
        self.assertIn(str(user.verification_token), mail.outbox[0].body)

    def test_verify_email_activates_user(self):
        token = uuid.uuid4()
        user = User.objects.create_user(
            email="mark@example.com",
            password="password123",
            first_name="Mark",
            last_name="Twain",
        )
        user.is_active = False
        user.is_verified = False
        user.verification_token = token
        user.verification_token_expires = timezone.now() + timedelta(hours=2)
        user.save()

        old_token = token
        response = self.client.get(reverse("accounts:verify_email", kwargs={"token": token}))
        self.assertRedirects(response, reverse("accounts:login"))

        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_verified)
        self.assertIsNone(user.verification_token_expires)
        self.assertNotEqual(user.verification_token, old_token)

    def test_resend_verification_creates_new_token_and_email(self):
        user = User.objects.create_user(
            email="mike@example.com",
            password="password123",
            first_name="Mike",
            last_name="Jones",
        )
        user.is_active = False
        user.is_verified = False
        user.verification_token = uuid.uuid4()
        user.verification_token_expires = timezone.now() + timedelta(hours=1)
        user.save()

        old_token = user.verification_token
        response = self.client.post(
            reverse("accounts:resend_verification"),
            {"email": user.email},
            follow=False,
        )
        self.assertRedirects(response, reverse("accounts:login"))

        user.refresh_from_db()
        self.assertNotEqual(old_token, user.verification_token)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(str(user.verification_token), mail.outbox[0].body)
