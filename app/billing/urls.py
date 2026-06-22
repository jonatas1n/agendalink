from django.urls import path

from . import views

urlpatterns = [
    path("choose-plan/", views.choose_plan, name="billing_choose_plan"),
    path("subscribe/", views.subscribe, name="billing_subscribe"),
]
