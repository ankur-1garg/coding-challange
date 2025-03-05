from django.db import models, transaction
from django.core.validators import MinValueValidator
from django.utils import timezone
import uuid
from django.conf import settings


class Order(models.Model):
    """Order model integrating Customer and Product services"""

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered')
    ]

    id = models.CharField(
        primary_key=True,
        max_length=36,
        default=uuid.uuid4,
        editable=False,
        help_text='Unique identifier for the order'
    )

    customer_id = models.CharField(
        max_length=36,
        db_index=True,
        help_text='Reference to customer in Customer service'
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text='Total order amount'
    )

    created_by = models.CharField(
        max_length=150,
        help_text='Username of the user who created the order'
    )

    updated_by = models.CharField(
        max_length=150,
        help_text='Username of the user who last updated the order'
    )

    class Meta:
        db_table = 'orders'
        indexes = [
            models.Index(fields=['customer_id']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at'])
        ]
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        """Ensure proper save with UUID and timestamps"""
        if not self.id:
            self.id = str(uuid.uuid4())
            if 'request' in kwargs:
                self.created_by = kwargs['request'].user.username
                kwargs.pop('request')
        if 'request' in kwargs:
            self.updated_by = kwargs['request'].user.username
            kwargs.pop('request')
        super().save(*args, **kwargs)

    @classmethod
    def create_with_items(cls, customer_id, items_data, request=None):
        """Create order with items in a single transaction"""
        with transaction.atomic():
            # Calculate total amount
            total_amount = sum(
                item['quantity'] * item['unit_price']
                for item in items_data
            )

            # Create order
            order = cls.objects.create(
                customer_id=customer_id,
                total_amount=total_amount,
                created_by=request.user.username if request else 'system',
                updated_by=request.user.username if request else 'system'
            )

            # Create order items
            for item_data in items_data:
                OrderItem.objects.create(
                    order=order,
                    **item_data
                )

            return order


class OrderItem(models.Model):
    """Order items linking products to orders"""

    id = models.CharField(
        primary_key=True,
        max_length=36,
        default=uuid.uuid4,
        editable=False
    )

    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE,
        help_text='Reference to parent order'
    )

    product_id = models.CharField(
        max_length=36,
        db_index=True,
        help_text='Reference to product in Product service'
    )

    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text='Quantity of product ordered'
    )

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text='Price of product at time of order'
    )

    line_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        help_text='Total price for this line item'
    )

    class Meta:
        db_table = 'order_items'
        indexes = [
            models.Index(fields=['product_id'])
        ]

    def save(self, *args, **kwargs):
        """Calculate line total before saving"""
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
