from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Product, Category, ProductImage
from .forms import ProductForm, ProductImageForm


def home(request):
    """Home page view."""
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:8]
    latest_products = Product.objects.filter(is_active=True).order_by("-created_at")[:8]
    
    context = {
        "featured_products": featured_products,
        "latest_products": latest_products,
    }
    return render(request, "store/home.html", context)


def shop(request):
    """Shop page with search and filtering."""
    products = Product.objects.filter(is_active=True)
    
    # Search
    search_query = request.GET.get("q", "")
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(short_description__icontains=search_query)
        )
    
    # Category filter
    category_slug = request.GET.get("category", "")
    if category_slug:
        try:
            category = Category.objects.get(slug=category_slug, is_active=True)
            products = products.filter(category=category)
        except Category.DoesNotExist:
            pass
    
    # Price range filter
    min_price = request.GET.get("min_price", "")
    max_price = request.GET.get("max_price", "")
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    # Availability filter
    in_stock = request.GET.get("in_stock", "")
    if in_stock == "true":
        products = products.filter(stock__gt=0)
    elif in_stock == "false":
        products = products.filter(stock=0)
    
    # Sorting
    sort_by = request.GET.get("sort", "newest")
    if sort_by == "price_low":
        products = products.order_by("price")
    elif sort_by == "price_high":
        products = products.order_by("-price")
    elif sort_by == "name":
        products = products.order_by("name")
    elif sort_by == "rating":
        products = products.annotate(
            avg_rating=Avg("reviews__rating")
        ).order_by("-avg_rating")
    else:  # newest
        products = products.order_by("-created_at")
    
    # Pagination
    paginator = Paginator(products, 12)  # 12 products per page
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    
    # Get all categories for filter
    categories = Category.objects.filter(is_active=True, parent=None)
    
    context = {
        "products": page_obj,
        "categories": categories,
        "search_query": search_query,
        "category_slug": category_slug,
        "min_price": min_price,
        "max_price": max_price,
        "in_stock": in_stock,
        "sort_by": sort_by,
    }
    
    return render(request, "store/shop.html", context)


def product_detail(request, slug):
    """Product detail page."""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    images = product.images.all()
    variations = product.variations.filter(is_active=True)
    
    # Get approved reviews
    reviews = product.reviews.filter(is_approved=True).order_by("-created_at")[:10]
    average_rating = product.get_average_rating()
    review_count = product.get_review_count()
    
    # Check if user can review
    can_review = False
    user_review = None
    if request.user.is_authenticated:
        user_review = product.reviews.filter(user=request.user).first()
        can_review = not user_review or not user_review.is_approved
    
    # Related products (same category)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    context = {
        "product": product,
        "images": images,
        "variations": variations,
        "reviews": reviews,
        "average_rating": average_rating,
        "review_count": review_count,
        "can_review": can_review,
        "user_review": user_review,
        "related_products": related_products,
    }
    
    return render(request, "store/product_detail.html", context)


def category_view(request, slug):
    """Category page view."""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(category=category, is_active=True)
    
    # Get subcategories
    subcategories = category.children.filter(is_active=True)
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        "category": category,
        "products": page_obj,
        "subcategories": subcategories,
    }
    
    return render(request, "store/category.html", context)


def about(request):
    """About page."""
    return render(request, "store/about.html")


def services(request):
    """Services page."""
    return render(request, "store/services.html")


def contact(request):
    """Contact page with form."""
    from marketing.forms import MarketingLeadForm
    from marketing.views import _notify_marketing_team
    
    if request.method == "POST":
        form = MarketingLeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.source = "Contact Page"
            lead.save()
            _notify_marketing_team(lead)
            messages.success(request, "Thanks! A specialist will contact you within one business day.")
            return redirect("store:contact")
    else:
        form = MarketingLeadForm()
    
    return render(request, "store/contact.html", {"form": form})


def terms(request):
    """Terms and conditions page."""
    return render(request, "store/terms.html")


def privacy(request):
    """Privacy notice page."""
    return render(request, "store/privacy.html")


def is_staff_user(user):
    """Check if user is staff/admin."""
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_staff_user)
def admin_product_list(request):
    """Admin view to list all products."""
    products = Product.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(sku__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        products = products.filter(is_active=True)
    elif status_filter == 'inactive':
        products = products.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'store/admin/product_list.html', context)


@login_required
@user_passes_test(is_staff_user)
def admin_product_create(request):
    """Admin view to create a new product."""
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            
            # Handle image uploads if any
            images = request.FILES.getlist('images')
            if images:
                for idx, image_file in enumerate(images):
                    ProductImage.objects.create(
                        product=product,
                        image=image_file,
                        is_primary=(idx == 0),  # First image is primary
                        order=idx
                    )
                messages.success(request, f'Product "{product.name}" created with {len(images)} image(s)!')
            else:
                messages.success(request, f'Product "{product.name}" created successfully!')
            
            return redirect('store:admin_product_update', pk=product.pk)
    else:
        form = ProductForm()
    
    context = {'form': form, 'action': 'Create', 'images': [], 'product': None}
    return render(request, 'store/admin/product_form.html', context)


@login_required
@user_passes_test(is_staff_user)
def admin_product_update(request, pk):
    """Admin view to update an existing product."""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('store:admin_product_list')
    else:
        form = ProductForm(instance=product)
    
    # Get existing images
    images = product.images.all()
    
    context = {'form': form, 'product': product, 'action': 'Update', 'images': images}
    return render(request, 'store/admin/product_form.html', context)


@login_required
@user_passes_test(is_staff_user)
def admin_product_delete(request, pk):
    """Admin view to delete a product."""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('store:admin_product_list')
    
    context = {'product': product}
    return render(request, 'store/admin/product_confirm_delete.html', context)


@login_required
@user_passes_test(is_staff_user)
def admin_product_image_add(request, pk):
    """Admin view to add an image to a product."""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.product = product
            image.save()
            messages.success(request, 'Image added successfully!')
            return redirect('store:admin_product_update', pk=product.pk)
    else:
        form = ProductImageForm()
    
    context = {'form': form, 'product': product}
    return render(request, 'store/admin/product_image_form.html', context)


@login_required
@user_passes_test(is_staff_user)
def admin_product_image_delete(request, pk):
    """Admin view to delete a product image."""
    image = get_object_or_404(ProductImage, pk=pk)
    product_pk = image.product.pk
    
    if request.method == 'POST':
        image.delete()
        messages.success(request, 'Image deleted successfully!')
        return redirect('store:admin_product_update', pk=product_pk)
    
    context = {'image': image}
    return render(request, 'store/admin/product_image_confirm_delete.html', context)
