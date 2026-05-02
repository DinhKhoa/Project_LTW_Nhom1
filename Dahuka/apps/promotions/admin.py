from django.contrib import admin
from .models import Promotion


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "discount_type", "value", "is_active", "status_display")
    list_filter = ("is_active", "discount_type", "start_date", "end_date")
    search_fields = ("name", "code")
    filter_horizontal = ("products",)
    readonly_fields = ("status_display",)
