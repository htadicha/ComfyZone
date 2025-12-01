from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("", views.home, name="home"),
    path("shop/", views.shop, name="shop"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("category/<slug:slug>/", views.category_view, name="category"),
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("contact/", views.contact, name="contact"),
    # Admin product management
    path("manage/products/", views.admin_product_list, name="admin_product_list"),
    path("manage/products/create/", views.admin_product_create, name="admin_product_create"),
    path("manage/products/<int:pk>/update/", views.admin_product_update, name="admin_product_update"),
    path("manage/products/<int:pk>/delete/", views.admin_product_delete, name="admin_product_delete"),
    # Admin product image management
    path("manage/products/<int:pk>/images/add/", views.admin_product_image_add, name="admin_product_image_add"),
    path("manage/products/images/<int:pk>/delete/", views.admin_product_image_delete, name="admin_product_image_delete"),
]

