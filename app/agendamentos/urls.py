from django.urls import path
from . import views

urlpatterns = [
    path("", views.list_appointments, name="list_appointments"),
    path("<int:pk>/", views.appointment_detail, name="appointment_detail"),
    path("<int:pk>/cancel/", views.cancel_appointment, name="cancel_appointment"),
    path(
        "<int:pk>/suggest-reschedule/",
        views.suggest_reschedule,
        name="suggest_reschedule",
    ),
]
