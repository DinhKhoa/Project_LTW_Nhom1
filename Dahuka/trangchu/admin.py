from django.contrib import admin
from .models import Customer, Address, Order, OrderItem

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone')
    list_filter = ('created_at',)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'customer', 'phone', 'address_type', 'is_default')
    search_fields = ('full_name', 'phone', 'customer__user__username')
    list_filter = ('address_type', 'is_default', 'created_at')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'total_amount', 'status', 'created_at')
    search_fields = ('order_number', 'customer__user__username')
    list_filter = ('status', 'created_at')
    readonly_fields = ('order_number', 'created_at')
    inlines = [OrderItemInline]
