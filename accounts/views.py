from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import UserRegistrationForm, UserLoginForm, ProfileUpdateForm, UserUpdateForm, AddressForm
from .models import Profile, Address
from .utils import send_verification_email, verify_email_token
from cart.utils import merge_carts


def register_view(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect("store:home")

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  # User can login before verification
            user.save()
            
            # Create profile
            Profile.objects.create(user=user)
            
            # Send verification email
            send_verification_email(user)
            
            messages.success(
                request,
                "Registration successful! Please check your email to verify your account."
            )
            return redirect("accounts:login")
    else:
        form = UserRegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    """User login view with cart merging."""
    if request.user.is_authenticated:
        return redirect("store:home")

    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                # Merge guest cart with user cart
                merge_carts(request, user)
                
                login(request, user)
                messages.success(request, f"Welcome back, {user.get_full_name() or user.email}!")
                
                next_url = request.GET.get("next", "store:home")
                return redirect(next_url)
            else:
                messages.error(request, "Invalid email or password.")
    else:
        form = UserLoginForm()

    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request):
    """User logout view."""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("store:home")


@require_http_methods(["GET"])
def verify_email_view(request, token):
    """Verify user email with token."""
    user = verify_email_token(token)
    
    if user:
        messages.success(request, "Email verified successfully! You can now log in.")
        return redirect("accounts:login")
    else:
        messages.error(request, "Invalid or expired verification link.")
        return redirect("accounts:login")


@login_required
def profile_view(request):
    """User profile view."""
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("accounts:profile")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)
    
    addresses = Address.objects.filter(user=request.user)
    
    return render(request, "accounts/profile.html", {
        "user_form": user_form,
        "profile_form": profile_form,
        "addresses": addresses,
    })


@login_required
def address_create_view(request):
    """Create new address."""
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, "Address added successfully!")
            return redirect("accounts:profile")
    else:
        form = AddressForm()
    
    return render(request, "accounts/address_form.html", {"form": form})


@login_required
def address_update_view(request, pk):
    """Update existing address."""
    address = Address.objects.get(pk=pk, user=request.user)
    
    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "Address updated successfully!")
            return redirect("accounts:profile")
    else:
        form = AddressForm(instance=address)
    
    return render(request, "accounts/address_form.html", {"form": form})


@login_required
def address_delete_view(request, pk):
    """Delete address."""
    address = Address.objects.get(pk=pk, user=request.user)
    if request.method == "POST":
        address.delete()
        messages.success(request, "Address deleted successfully!")
    return redirect("accounts:profile")
