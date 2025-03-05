from django.contrib import admin
from django.utils.html import format_html
from django.core.exceptions import PermissionDenied
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone',
                    'status_badge', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'phone')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'email')
        }),
        ('Contact Details', {
            'fields': ('phone',)
        }),
        ('Status Information', {
            'fields': ('status', 'created_at', 'updated_at')
        })
    )

    def status_badge(self, obj):
        """Display status with color coding"""
        colors = {
            'ACTIVE': 'green',
            'INACTIVE': 'orange',
            'BLOCKED': 'red'
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def has_module_permission(self, request):
        """Only allow staff members to see this module"""
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        """Only allow staff members to view customers"""
        return request.user.is_staff

    def has_add_permission(self, request):
        """Only allow superusers to add customers"""
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        """Only allow superusers to edit customers"""
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        """Disable deletion completely"""
        return False

    def get_actions(self, request):
        """Only show actions to superusers"""
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            return []
        return actions

    def save_model(self, request, obj, form, change):
        """Log changes and validate permissions before saving"""
        if not request.user.is_superuser:
            raise PermissionDenied("Only superusers can modify customers")
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        """Make all fields readonly for non-superusers"""
        if not request.user.is_superuser:
            return [field.name for field in self.model._meta.fields]
        return self.readonly_fields

    actions = ['make_active', 'make_inactive', 'make_blocked']

    def make_active(self, request, queryset):
        updated = queryset.update(status='ACTIVE')
        self.message_user(request, f'{updated} customers marked as active.')
    make_active.short_description = "Mark selected customers as active"

    def make_inactive(self, request, queryset):
        updated = queryset.update(status='INACTIVE')
        self.message_user(request, f'{updated} customers marked as inactive.')
    make_inactive.short_description = "Mark selected customers as inactive"

    def make_blocked(self, request, queryset):
        updated = queryset.update(status='BLOCKED')
        self.message_user(request, f'{updated} customers marked as blocked.')
    make_blocked.short_description = "Mark selected customers as blocked"
