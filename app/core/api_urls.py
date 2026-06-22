from django.urls import path
from produtos import api as products_api
from agendamentos import api as appointments_api
from billing import api as billing_api
from core import api as core_api

urlpatterns = [
    path("store/slug-check/", core_api.check_store_slug, name="api_check_store_slug"),
    path("products/", products_api.list_products, name="api_products"),
    path("products/<int:pk>/", products_api.product_detail, name="api_product_detail"),
    path(
        "products/<int:pk>/availability/",
        products_api.product_availability,
        name="api_availability",
    ),
    path(
        "appointments/check/",
        appointments_api.check_availability,
        name="api_check_availability",
    ),
    path(
        "appointments/create/",
        appointments_api.create_appointment,
        name="api_create_appointment",
    ),
    path(
        "appointments/mine/",
        appointments_api.my_appointments,
        name="api_my_appointments",
    ),
    path(
        "appointments/<int:pk>/cancel/",
        appointments_api.cancel_appointment,
        name="api_cancel_appointment",
    ),
    path(
        "appointments/<int:pk>/phone/",
        appointments_api.update_appointment_phone,
        name="api_appointment_phone",
    ),
    path("billing/asaas/webhook/", billing_api.asaas_webhook, name="api_asaas_webhook"),
]
