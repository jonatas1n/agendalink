from django.urls import path
from . import views

urlpatterns = [
    path("", views.list_products, name="list_products"),
    path("new/", views.create_product, name="create_product"),
    path("<int:pk>/", views.product_detail, name="product_detail"),
    path("<int:pk>/edit/", views.edit_product, name="edit_product"),
    path("<int:pk>/delete/", views.delete_product, name="delete_product"),
    path("<int:pk>/book/", views.book_product, name="book_product"),
    path(
        "<int:pk>/availability/", views.manage_availability, name="manage_availability"
    ),
]
