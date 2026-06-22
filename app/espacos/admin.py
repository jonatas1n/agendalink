from django.contrib import admin

from .models import Space, SpaceMember


class MemberInline(admin.TabularInline):
    model = SpaceMember
    extra = 0
    fields = ["user", "role", "status", "specialty"]


@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    list_display = ["name", "admin", "collective_schedule_active", "active"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [MemberInline]


@admin.register(SpaceMember)
class SpaceMemberAdmin(admin.ModelAdmin):
    list_display = ["user", "space", "role", "status"]
    list_filter = ["space", "status", "role"]
