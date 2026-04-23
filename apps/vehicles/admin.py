from django.contrib import admin
from .models import Vehicle

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('number', 'driver')
    list_filter = ('driver',)
    search_fields = ('number', 'driver__username')