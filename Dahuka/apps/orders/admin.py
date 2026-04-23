from django.contrib import admin
from .models import Order, OrderItem
from apps.tasks.models import InstallationTask

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class InstallationTaskInline(admin.StackedInline):
    model = InstallationTask
    extra = 0
    max_num = 1
    can_delete = False
    fields = ('assigned_staff', 'status', 'note', 'completed_at')
    readonly_fields = ('created_at',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'phone', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'phone')
    inlines = [OrderItemInline, InstallationTaskInline]
