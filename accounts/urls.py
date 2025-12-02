from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("verify-email/<uuid:token>/", views.verify_email_view, name="verify_email"),
    path("resend-verification/", views.resend_verification_view, name="resend_verification"),
    path("address/create/", views.address_create_view, name="address_create"),
    path("address/<int:pk>/update/", views.address_update_view, name="address_update"),
    path("address/<int:pk>/delete/", views.address_delete_view, name="address_delete"),
]
