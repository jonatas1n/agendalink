from django.contrib import admin

from .models import (
    DateAvailability,
    DateBlock,
    Product,
    ProductPrice,
    UnavailablePeriod,
    WeeklyAvailability,
)


class WeeklyAvailabilityInline(admin.TabularInline):
    model = WeeklyAvailability
    extra = 1


class ProductPriceInline(admin.TabularInline):
    model = ProductPrice
    extra = 0
    fields = ["sort_order", "label", "duration_minutes", "price"]


class DateBlockInline(admin.TabularInline):
    model = DateBlock
    extra = 0


class UnavailablePeriodInline(admin.TabularInline):
    model = UnavailablePeriod
    extra = 0


class DateAvailabilityInline(admin.TabularInline):
    model = DateAvailability
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "price_type", "price", "active"]
    list_filter = ["price_type", "active"]
    inlines = [
        ProductPriceInline,
        WeeklyAvailabilityInline,
        UnavailablePeriodInline,
        DateAvailabilityInline,
        DateBlockInline,
    ]


@admin.register(WeeklyAvailability)
class WeeklyAvailabilityAdmin(admin.ModelAdmin):
    list_display = ["product", "weekday", "start_time", "end_time"]


@admin.register(DateBlock)
class DateBlockAdmin(admin.ModelAdmin):
    list_display = ["product", "date", "reason"]
