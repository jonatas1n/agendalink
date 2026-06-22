from django.contrib import admin

from .models import StoreProfile


@admin.register(StoreProfile)
class StoreProfileAdmin(admin.ModelAdmin):
    list_display = ("display_name", "slug", "public_id", "user", "city", "updated_at")
    search_fields = ("name", "slug", "public_id", "user__username", "user__email")
    raw_id_fields = ("user",)
