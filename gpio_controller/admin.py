from django.contrib import admin
from .models import GPIOConnection, JetsonNanoDevice


@admin.register(GPIOConnection)
class GPIOConnectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'reset', 'force_recovery', 'is_enabled', 'created_at')
    list_filter = ('is_enabled', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Connection Information', {
            'fields': ('name', 'description', 'is_enabled')
        }),
        ('GPIO Pins', {
            'fields': ('reset', 'force_recovery'),
            'description': 'Physical GPIO pin numbers in BCM mode'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(JetsonNanoDevice)
class JetsonNanoDeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'connected_to', 'usb_connection', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Device Information', {
            'fields': ('name', 'description', 'usb_connection', 'is_active')
        }),
        ('Connection', {
            'fields': ('connected_to',),
            'description': 'GPIO connection this device is wired to'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
