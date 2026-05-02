from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("price",)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "session_key", "created_at", "updated_at", "total_price")
    list_filter = ("created_at",)
    search_fields = ("user__username", "session_key")
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity", "price", "subtotal")
    list_filter = ("created_at",)
    search_fields = ("product__name", "cart__user__username")
