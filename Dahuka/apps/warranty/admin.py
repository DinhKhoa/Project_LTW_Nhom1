from django.contrib import admin
from .models import WarrantyPageSettings

@admin.register(WarrantyPageSettings)
class WarrantyPageSettingsAdmin(admin.ModelAdmin):
    list_display = ('title',)
