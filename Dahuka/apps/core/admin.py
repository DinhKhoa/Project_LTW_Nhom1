from django.contrib import admin
from .models import HomePageSettings
from apps.account.models import Customer, Address
from apps.orders.models import Order, OrderItem

@admin.register(HomePageSettings)
class HomePageSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__',)

# Note: Customer, Address, Order, OrderItem should be registered in their respective admin.py
# I will move them there to follow Django best practices (Task 6/7)
