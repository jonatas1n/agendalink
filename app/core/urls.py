from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from produtos import views as product_views

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.landing, name="landing"),
    path("auth/", include("django.contrib.auth.urls")),
    path("auth/cadastro/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/store/", views.store_settings, name="store_settings"),
    path("loja/<slug:store_slug>/", views.public_store, name="public_store"),
    path(
        "loja/<slug:store_slug>/servico/<int:pk>/",
        product_views.book_store_product,
        name="book_store_product",
    ),
    path("dashboard/billing/", include("billing.urls")),
    path("products/", include("produtos.urls")),
    path("appointments/", include("agendamentos.urls")),
    path("api/", include("core.api_urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
