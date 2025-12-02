from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    path("product/<slug:product_slug>/", views.product_reviews, name="product_reviews"),
    path("manage/<slug:product_slug>/", views.manage_review, name="manage"),
    path("create/<slug:product_slug>/", views.create_review, name="create"),
    path("update/<int:review_id>/", views.update_review, name="update"),
    path("delete/<int:review_id>/", views.delete_review, name="delete"),
]
