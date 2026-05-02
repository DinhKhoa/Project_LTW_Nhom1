from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ("product", "quantity", "price", "warranty_expiration")
    readonly_fields = ("warranty_expiration",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_code",
        "full_name",
        "phone",
        "total_amount",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("order_code", "full_name", "phone")
    readonly_fields = ("order_code",)
    inlines = [OrderItemInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.status == "completed":
            from .services import OrderService

            OrderService.process_warranty(obj)
