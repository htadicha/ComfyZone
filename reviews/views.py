from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from store.models import Product
from .forms import ReviewForm
from .models import Review


@login_required
@require_http_methods(["GET", "POST"])
def manage_review(request, product_slug):
    """Single entry point for creating, updating, and deleting a review."""
    product = get_object_or_404(Product, slug=product_slug, is_active=True)
    review = Review.objects.filter(product=product, user=request.user).first()
    recent_reviews = Review.objects.filter(product=product, is_approved=True).order_by("-created_at")[:5]

    action = request.POST.get("action")
    if action == "delete":
        if review:
            review.delete()
            messages.success(request, "Review deleted successfully.")
        else:
            messages.info(request, "You don't have a review for this product yet.")
        return redirect("store:product_detail", slug=product.slug)

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            created = review is None
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.is_approved = False
            review.save()

            if created:
                messages.success(request, "Thank you for your review! It will be published after moderation.")
            else:
                messages.success(request, "Review updated! It will be republished after moderation.")
            return redirect("reviews:manage", product_slug=product.slug)
    else:
        form = ReviewForm(instance=review)

    return render(
        request,
        "reviews/form.html",
        {
            "form": form,
            "product": product,
            "review": review,
            "recent_reviews": recent_reviews,
            "has_review": review is not None,
        },
    )


@login_required
def create_review(request, product_slug):
    """Backwards compatible endpoint forwarding to manage_review."""
    return manage_review(request, product_slug)


@login_required
def update_review(request, review_id):
    """Redirect legacy update route to the unified manage view."""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    return manage_review(request, product_slug=review.product.slug)


@login_required
@require_http_methods(["POST"])
def delete_review(request, review_id):
    """Delete review."""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product_slug = review.product.slug
    review.delete()

    messages.success(request, "Review deleted successfully.")
    if request.POST.get("return_to") == "manage":
        return redirect("reviews:manage", product_slug=product_slug)
    return redirect("store:product_detail", slug=product_slug)


def product_reviews(request, product_slug):
    """View all reviews for a product."""
    product = get_object_or_404(Product, slug=product_slug, is_active=True)
    reviews = Review.objects.filter(product=product, is_approved=True).order_by("-created_at")

    can_review = False
    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(product=product, user=request.user).first()
        can_review = not user_review or not user_review.is_approved

    return render(request, "reviews/list.html", {
        "product": product,
        "reviews": reviews,
        "can_review": can_review,
        "user_review": user_review,
    })
