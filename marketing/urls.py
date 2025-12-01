from django.urls import path
from . import views

app_name = "marketing"

urlpatterns = [
    path("subscribe/", views.subscribe, name="subscribe"),
    path("unsubscribe/<str:email>/", views.unsubscribe, name="unsubscribe"),
]


