from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from store.models import Product
from .models import Review
from .forms import ReviewForm


@login_required
def create_review(request, product_slug):
    """Create or update product review."""
    product = get_object_or_404(Product, slug=product_slug, is_active=True)
    
    # Check if review already exists (don't create it yet)
    try:
        review = Review.objects.get(product=product, user=request.user)
    except Review.DoesNotExist:
        review = None
    
    if request.method == "POST":
        if review:
            form = ReviewForm(request.POST, instance=review)
        else:
            form = ReviewForm(request.POST)
        
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.is_approved = False  # Require moderation
            review.save()
            
            messages.success(request, "Thank you for your review! It will be published after moderation.")
            return redirect("store:product_detail", slug=product.slug)
    else:
        if review:
            form = ReviewForm(instance=review)
        else:
            form = ReviewForm()
    
    return render(request, "reviews/form.html", {
        "form": form,
        "product": product,
        "review": review,
    })


@login_required
def update_review(request, review_id):
    """Update existing review."""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            review = form.save(commit=False)
            review.is_approved = False  # Require re-moderation after edit
            review.save()
            
            messages.success(request, "Review updated! It will be republished after moderation.")
            return redirect("store:product_detail", slug=review.product.slug)
    else:
        form = ReviewForm(instance=review)
    
    return render(request, "reviews/form.html", {
        "form": form,
        "product": review.product,
        "review": review,
    })


@login_required
@require_http_methods(["POST"])
def delete_review(request, review_id):
    """Delete review."""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product_slug = review.product.slug
    review.delete()
    
    messages.success(request, "Review deleted successfully.")
    return redirect("store:product_detail", slug=product_slug)


def product_reviews(request, product_slug):
    """View all reviews for a product."""
    product = get_object_or_404(Product, slug=product_slug, is_active=True)
    reviews = Review.objects.filter(product=product, is_approved=True).order_by("-created_at")
    
    # Check if user can review
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
