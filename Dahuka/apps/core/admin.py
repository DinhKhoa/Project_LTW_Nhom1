from django.contrib import admin
from .models import HomePageSettings

@admin.register(HomePageSettings)
class HomePageSettingsAdmin(admin.ModelAdmin):
    list_display = ("__str__",)
