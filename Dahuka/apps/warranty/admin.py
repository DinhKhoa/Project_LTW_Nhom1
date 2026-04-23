from django.contrib import admin
from .models import WarrantyCard, MaintenanceHistory

class MaintenanceHistoryInline(admin.TabularInline):
    model = MaintenanceHistory
    extra = 1

@admin.register(WarrantyCard)
class WarrantyCardAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'product', 'customer', 'activated_date', 'expiry_date', 'is_active')
    list_filter = ('is_active', 'activated_date', 'product')
    search_fields = ('serial_number', 'customer__username', 'customer__first_name', 'customer__last_name')
    inlines = [MaintenanceHistoryInline]
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('serial_number', 'product', 'customer')
        }),
        ('Chi tiết bảo hành', {
            'fields': ('activated_date', 'expiry_date', 'is_active')
        }),
    )

@admin.register(MaintenanceHistory)
class MaintenanceHistoryAdmin(admin.ModelAdmin):
    list_display = ('warranty_card', 'date', 'technician', 'next_maintenance_date')
    list_filter = ('date', 'technician')
    search_fields = ('warranty_card__serial_number', 'technician')
