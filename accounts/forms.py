from django import forms
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from .models import User, Profile, Address


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column("email", css_class="form-group col-md-12 mb-3"),
                css_class="form-row"
            ),
            Row(
                Column("first_name", css_class="form-group col-md-6 mb-3"),
                Column("last_name", css_class="form-group col-md-6 mb-3"),
                css_class="form-row"
            ),
            Row(
                Column("password1", css_class="form-group col-md-6 mb-3"),
                Column("password2", css_class="form-group col-md-6 mb-3"),
                css_class="form-row"
            ),
            Submit("submit", "Register", css_class="btn btn-primary")
        )


class UserLoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            "email",
            "password",
            Submit("submit", "Login", css_class="btn btn-primary")
        )


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["phone_number", "profile_picture", "date_of_birth", "bio"]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "bio": forms.Textarea(attrs={"rows": 4}),
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            "address_type",
            "first_name",
            "last_name",
            "company_name",
            "street_address",
            "apartment_address",
            "city",
            "state",
            "postal_code",
            "country",
            "phone",
            "is_default",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            "address_type",
            Row(
                Column("first_name", css_class="form-group col-md-6 mb-3"),
                Column("last_name", css_class="form-group col-md-6 mb-3"),
                css_class="form-row"
            ),
            "company_name",
            "street_address",
            "apartment_address",
            Row(
                Column("city", css_class="form-group col-md-6 mb-3"),
                Column("state", css_class="form-group col-md-6 mb-3"),
                css_class="form-row"
            ),
            Row(
                Column("postal_code", css_class="form-group col-md-6 mb-3"),
                Column("country", css_class="form-group col-md-6 mb-3"),
                css_class="form-row"
            ),
            "phone",
            "is_default",
            Submit("submit", "Save Address", css_class="btn btn-primary")
        )


class ResendVerificationForm(forms.Form):
    """Form used to request a new verification email."""

    email = forms.EmailField(label="Account email address", required=True)

    def __init__(self, *args, **kwargs):
        self.user = None
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            "email",
            Submit("submit", "Send verification link", css_class="btn btn-primary"),
        )

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        try:
            self.user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError("We couldn't find an account with that email.")

        if self.user.is_verified:
            raise forms.ValidationError("This account has already been verified.")

        return email
