from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import MarketingLead, NewsletterSubscriber


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend", DEFAULT_FROM_EMAIL="test@example.com")
class NewsletterTests(TestCase):
    def test_subscribe_creates_inactive_record_and_sends_email(self):
        """Ensure subscribe creates inactive subscriber and sends email."""
        response = self.client.post(
            reverse("marketing:subscribe"),
            {"email": "hello@example.com", "name": "Hello", "consent": True},
            follow=False,
        )
        self.assertRedirects(response, "/")
        subscriber = NewsletterSubscriber.objects.get(email="hello@example.com")
        self.assertFalse(subscriber.is_active)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(str(subscriber.confirmation_token), mail.outbox[0].body)

    def test_confirm_subscription_activates_user(self):
        """Ensure confirmation token activates subscriber."""
        subscriber = NewsletterSubscriber.objects.create(
            email="hello@example.com",
            name="Hello",
            consent=True,
            consent_text="test",
            is_active=False,
        )
        response = self.client.get(reverse("marketing:confirm_subscription", args=[subscriber.confirmation_token]))
        self.assertRedirects(response, "/")
        subscriber.refresh_from_db()
        self.assertTrue(subscriber.is_active)
        self.assertIsNotNone(subscriber.confirmed_at)


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend", DEFAULT_FROM_EMAIL="test@example.com")
class MarketingLeadTests(TestCase):
    def test_lead_form_requires_consent(self):
        """Ensure consent is required for lead submissions."""
        response = self.client.post(
            reverse("marketing:lead_create"),
            {"name": "Jane", "email": "jane@example.com", "interest": "Sofa refresh", "consent": False},
        )
        self.assertContains(response, "consent", status_code=200)
        self.assertEqual(MarketingLead.objects.count(), 0)

    def test_lead_form_records_entry(self):
        """Ensure a valid lead creates a record and sends email."""
        response = self.client.post(
            reverse("marketing:lead_create"),
            {
                "name": "Jane",
                "email": "jane@example.com",
                "interest": "Sofa refresh",
                "consent": True,
            },
        )
        self.assertRedirects(response, reverse("store:home"))
        self.assertEqual(MarketingLead.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

    def test_lead_dashboard_requires_staff(self):
        """Ensure non-staff are redirected from lead dashboard."""
        non_staff = get_user_model().objects.create_user(email="user@example.com", password="test12345")
        self.client.force_login(non_staff)
        response = self.client.get(reverse("marketing:lead_list"))
        self.assertEqual(response.status_code, 302)

    def test_lead_dashboard_for_staff(self):
        """Ensure staff can access the lead dashboard."""
        staff = get_user_model().objects.create_user(email="staff@example.com", password="test12345", is_staff=True)
        self.client.force_login(staff)
        response = self.client.get(reverse("marketing:lead_list"))
        self.assertEqual(response.status_code, 200)
