from django.urls import path
from . import views

urlpatterns = [
    path("<slug:slug>/", views.public_space, name="public_space"),
    path(
        "<slug:slug>/professional/<int:member_id>/",
        views.public_professional,
        name="public_professional",
    ),
    path(
        "<slug:slug>/book/<int:product_id>/",
        views.book_conversation,
        name="book_conversation",
    ),
    path("my/new/", views.create_space, name="create_space"),
    path("my/<slug:slug>/edit/", views.edit_space, name="edit_space"),
    path("my/<slug:slug>/members/", views.manage_members, name="manage_members"),
    path(
        "my/<slug:slug>/schedule/",
        views.collective_schedule,
        name="collective_schedule",
    ),
]
