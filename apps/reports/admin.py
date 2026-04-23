from django.contrib import admin
from django.utils.html import format_html
from .models import WashReport, ServiceReport

class BaseReportAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'created_at', 'photo_preview')
    list_filter = ('vehicle__driver', 'created_at')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="100" />', obj.photo.url)
        return '-'
    photo_preview.short_description = 'Превью фото'

@admin.register(WashReport)
class WashReportAdmin(BaseReportAdmin):
    pass

@admin.register(ServiceReport)
class ServiceReportAdmin(BaseReportAdmin):
    pass