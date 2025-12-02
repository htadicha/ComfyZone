from django.urls import path
from . import views

app_name = "marketing"

urlpatterns = [
    path("subscribe/", views.subscribe, name="subscribe"),
    path("subscribe/confirm/<uuid:token>/", views.confirm_subscription, name="confirm_subscription"),
    path("unsubscribe/<uuid:token>/", views.unsubscribe, name="unsubscribe"),
    path("leads/new/", views.lead_create_view, name="lead_create"),
    path("leads/", views.lead_list_view, name="lead_list"),
]
