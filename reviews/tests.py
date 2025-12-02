from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from store.models import Category, Product
from .models import Review


class ReviewManageViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="buyer@example.com",
            password="password123",
            first_name="Buyer",
            last_name="Test",
        )
        self.category = Category.objects.create(name="Living Room")
        self.product = Product.objects.create(
            name="Cozy Sofa",
            slug="cozy-sofa",
            description="Comfortable sofa",
            price=999.99,
            stock=10,
            category=self.category,
        )
        self.manage_url = reverse("reviews:manage", kwargs={"product_slug": self.product.slug})

    def test_create_review_via_manage_view(self):
        self.client.force_login(self.user)

        response = self.client.post(
            self.manage_url,
            {"title": "Great!", "comment": "Loved it", "rating": 5},
            follow=False,
        )

        self.assertRedirects(response, self.manage_url)
        review = Review.objects.get(product=self.product, user=self.user)
        self.assertEqual(review.rating, 5)
        self.assertFalse(review.is_approved)

    def test_update_review_sets_back_to_pending(self):
        review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=4,
            title="Nice",
            comment="Pretty good",
            is_approved=True,
        )
        self.client.force_login(self.user)

        response = self.client.post(
            self.manage_url,
            {"title": "Updated", "comment": "Even better", "rating": 5},
            follow=False,
        )
        self.assertRedirects(response, self.manage_url)

        review.refresh_from_db()
        self.assertEqual(review.title, "Updated")
        self.assertFalse(review.is_approved)

    def test_delete_review_via_manage_view(self):
        Review.objects.create(
            product=self.product,
            user=self.user,
            rating=3,
            title="Okay",
            comment="It was fine",
        )
        self.client.force_login(self.user)

        response = self.client.post(
            self.manage_url,
            {"action": "delete"},
            follow=False,
        )
        self.assertRedirects(response, reverse("store:product_detail", kwargs={"slug": self.product.slug}))
        self.assertFalse(Review.objects.filter(product=self.product, user=self.user).exists())
