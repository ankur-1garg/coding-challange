from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'stock')
    list_filter = ('stock',)
    search_fields = ('name',)
    ordering = ('name',)
    readonly_fields = ('id',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'price')
        }),
        ('Inventory', {
            'fields': ('stock',),
            'classes': ('collapse',)
        }),
    )

    def has_delete_permission(self, request, obj=None):
        # Prevent accidental deletion of products
        return False

    def save_model(self, request, obj, form, change):
        if change:  # If this is an update
            original = Product.objects.get(pk=obj.pk)
            if original.stock != obj.stock:
                self.message_user(
                    request,
                    f"Stock changed from {original.stock} to {obj.stock}"
                )
        super().save_model(request, obj, form, change)
