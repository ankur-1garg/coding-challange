from django.db import models
import uuid
from django.core.validators import MinValueValidator
from django.utils import timezone
import requests
from django.conf import settings
from .exceptions import InsufficientStockError, ProductNotFoundError
from django.core.exceptions import ValidationError


class Order(models.Model):
    """Order model with Snowflake integration"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('delivered', 'Delivered'),
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
        help_text='Reference to Customer from Customer Service'
    )

    product_id = models.CharField(
        max_length=36,
        help_text='Reference to Product from Product Service'
    )

    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text='Number of items ordered'
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        help_text='Total price of the order'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text='Current status of the order'
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        help_text='Timestamp when the order was created'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Timestamp when the order was last updated'
    )

    class Meta:
        db_table = 'ORDERS'  # Note: Snowflake table names are case-sensitive
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer_id'], name='order_customer_idx'),
            models.Index(fields=['product_id'], name='order_product_idx'),
            models.Index(fields=['status'], name='order_status_idx'),
            models.Index(fields=['created_at'], name='order_created_idx'),
        ]

    def __str__(self):
        return f"Order {self.id} - Customer {self.customer_id}"

    def save(self, *args, **kwargs):
        """Override save to ensure proper validation and service communication"""
        token = kwargs.pop('token', None)
        if not token and not self.id:  # Only require token for new orders
            raise ValidationError("Token is required for order creation")

        # Always generate ID for new orders
        if not self.id:
            self.id = str(uuid.uuid4())

        if token and not self.total_price:
            headers = {
                'Authorization': f'Token {token}',
                'Content-Type': 'application/json'
            }

            try:
                # Get product price
                response = requests.get(
                    f"{settings.PRODUCT_SERVICE_URL}/api/products/{self.product_id}/",
                    headers=headers,
                    timeout=5
                )

                if response.status_code == 200:
                    product_data = response.json()
                    self.total_price = float(
                        product_data['price']) * self.quantity
                else:
                    raise ValidationError("Could not fetch product details")

            except Exception as e:
                raise ValidationError(
                    f"Error calculating total price: {str(e)}")

        super().save(*args, **kwargs)
