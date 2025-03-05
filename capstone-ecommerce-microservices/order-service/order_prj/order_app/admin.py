from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('id', 'line_total')
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_id', 'status',
                    'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'customer_id')
    readonly_fields = ('id', 'created_at')
    inlines = [OrderItemInline]

    def has_delete_permission(self, request, obj=None):
        return False
