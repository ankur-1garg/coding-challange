from django.core.exceptions import ValidationError
from .exceptions import (
    InsufficientStockError,
    ProductNotFoundError,
    ProductServiceError,
    OrderError
)
from django.db import models, transaction
import uuid
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.utils import timezone
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class Order(models.Model):
    """Order model with Snowflake integration"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
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
        help_text='Reference to Customer from Customer Service',
        null=False
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Total price of the order',
        null=False
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text='Current status of the order',
        null=False
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        help_text='Timestamp when the order was created',
        null=False
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Timestamp when the order was last updated',
        null=False
    )

    class Meta:
        db_table = 'ORDERS'  # Note: Snowflake table names are case-sensitive
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer_id'], name='order_customer_idx'),
            models.Index(fields=['status'], name='order_status_idx'),
            models.Index(fields=['created_at'], name='order_created_idx'),
        ]

    def __str__(self):
        return f"Order {self.id} - Customer {self.customer_id}"

    def save(self, *args, **kwargs):
        """Override save to handle customer statistics updates"""
        is_new = not self.id
        with transaction.atomic():
            # Generate ID for new orders
            if not self.id:
                self.id = str(uuid.uuid4())

            # Call parent save
            super().save(*args, **kwargs)

            # Update customer statistics for new orders
            if is_new and 'token' in kwargs:
                self.update_customer_statistics(kwargs['token'])

    def update_customer_statistics(self, token):
        """Update customer's last order date and total orders"""
        headers = {
            'Authorization': f'Token {token}',
            'Content-Type': 'application/json'
        }

        try:
            # Get current customer stats
            customer_response = requests.get(
                f"{settings.CUSTOMER_SERVICE_URL}/api/customers/{self.customer_id}/",
                headers=headers,
                timeout=5
            )
            customer_response.raise_for_status()

            # Prepare update data
            update_data = {
                'last_order_date': timezone.now().isoformat(),
                'total_orders': customer_response.json().get('total_orders', 0) + 1
            }

            # Update customer statistics
            update_response = requests.patch(
                f"{settings.CUSTOMER_SERVICE_URL}/api/customers/{self.customer_id}/",
                headers=headers,
                json=update_data,
                timeout=5
            )
            update_response.raise_for_status()
            logger.info(
                f"Updated customer {self.customer_id} statistics: {update_data}")

        except requests.RequestException as e:
            logger.error(f"Failed to update customer statistics: {str(e)}")
            raise ProductServiceError(
                f"Error updating customer statistics: {str(e)}")


class OrderItem(models.Model):
    id = models.CharField(primary_key=True, max_length=36,
                          default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order, related_name='items', on_delete=models.CASCADE, null=False)
    product_id = models.CharField(max_length=36, null=False)
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], null=False)
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=False)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, null=False)

    class Meta:
        db_table = 'ORDER_ITEMS'
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['product_id'])
        ]

    def save(self, *args, **kwargs):
        if not self.subtotal:
            self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def update_product_stock(self, token):
        """Update product stock in product service"""
        headers = {
            'Authorization': f'Token {token}',
            'Content-Type': 'application/json'
        }

        # Get current product stock
        try:
            product_response = requests.get(
                f"{settings.PRODUCT_SERVICE_URL}/api/products/{self.product_id}/",
                headers=headers,
                timeout=5
            )
            product_response.raise_for_status()
            product = product_response.json()

            # Calculate new stock
            new_stock = product['stock'] - self.quantity
            if new_stock < 0:
                raise InsufficientStockError(
                    f"Insufficient stock. Available: {product['stock']}, Requested: {self.quantity}"
                )

            # Update product stock
            update_response = requests.patch(
                f"{settings.PRODUCT_SERVICE_URL}/api/products/{self.product_id}/",
                headers=headers,
                json={'stock': new_stock},
                timeout=5
            )
            update_response.raise_for_status()

            return True

        except requests.exceptions.RequestException as e:
            raise ProductServiceError(
                f"Error communicating with product service: {str(e)}")
