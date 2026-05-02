from django.contrib import admin
from .models import Customer, Address

class AddressInline(admin.StackedInline):
    model = Address
    extra = 0

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')
    search_fields = ('user__username', 'phone')
    inlines = [AddressInline]

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'customer', 'province', 'district', 'is_default')
    list_filter = ('province', 'is_default')
    search_fields = ('full_name', 'phone')
