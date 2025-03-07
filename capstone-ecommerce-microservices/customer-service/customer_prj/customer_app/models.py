from django.db import models
from django.core.validators import EmailValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid
import json


class Customer(models.Model):
    """Customer model for e-commerce platform with microservice integration"""

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('BLOCKED', 'Blocked')
    ]

    id = models.CharField(
        primary_key=True,
        max_length=36,
        default=uuid.uuid4,
        editable=False,
        help_text='Unique identifier for the customer'
    )

    email = models.EmailField(
        unique=True,
        validators=[
            EmailValidator(message='Enter a valid email address.')
        ],
        error_messages={
            'unique': 'A customer with this email already exists.',
            'blank': 'Email address is required.',
            'null': 'Email address cannot be null.'
        }
    )

    name = models.CharField(
        max_length=100,
        help_text='Customer full name',
        error_messages={
            'blank': 'Customer name is required.',
            'max_length': 'Name cannot exceed 100 characters.'
        }
    )

    phone = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message='Phone number must be in format: "+999999999". Up to 15 digits allowed.'
            )
        ],
        blank=True,
        help_text='Contact phone number in international format'
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='ACTIVE',
        help_text='Current status of the customer account'
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        help_text='Timestamp when the customer was created'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Timestamp when the customer was last updated'
    )

    # Add new fields for service integration
    last_order_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Date of customer\'s last order'
    )

    total_orders = models.IntegerField(
        default=0,
        help_text='Total number of orders placed by customer'
    )

    class Meta:
        db_table = 'CUSTOMERS'
        managed = False  # Let Snowflake manage the table

    def __str__(self):
        return f"{self.name} ({self.email})"

    def clean(self):
        """
        Custom validation for the Customer model.
        Raises ValidationError if validation fails.
        """
        if not self.name or not self.name.strip():
            raise ValidationError(
                {'name': 'Name cannot be empty or whitespace only.'})

        if len(self.name.strip()) < 2:
            raise ValidationError(
                {'name': 'Name must be at least 2 characters long.'})

        if self.phone and not self.phone.startswith('+'):
            raise ValidationError(
                {'phone': 'Phone number must start with "+" for international format.'})

    def save(self, *args, **kwargs):
        """
        Override save method to ensure validation is always run
        and data is cleaned before saving.
        """
        self.full_clean()
        if self.name:
            self.name = self.name.strip()
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        """Check if customer account is active"""
        return self.status == 'ACTIVE'

    @property
    def is_blocked(self):
        """Check if customer account is blocked"""
        return self.status == 'BLOCKED'

    def activate(self):
        """Activate customer account"""
        if self.status != 'ACTIVE':
            self.status = 'ACTIVE'
            self.save()

    def deactivate(self):
        """Deactivate customer account"""
        if self.status != 'INACTIVE':
            self.status = 'INACTIVE'
            self.save()

    def block(self):
        """Block customer account"""
        if self.status != 'BLOCKED':
            self.status = 'BLOCKED'
            self.save()

    def change_status(self, new_status):
        """Change customer status if different from current"""
        if new_status in dict(self.STATUS_CHOICES) and self.status != new_status:
            self.status = new_status
            self.save()

    def to_dict(self):
        """
        Convert customer data to dictionary for service communication
        Excludes sensitive information
        """
        return {
            'customer_id': str(self.id),
            'email': self.email,
            'name': self.name,
            'status': self.status,
            'is_active': self.is_active,
            'total_orders': self.total_orders
        }

    def to_json(self):
        """Convert customer data to JSON for API responses"""
        return json.dumps(self.to_dict())

    def update_order_stats(self, order_date):
        """Update customer's order statistics"""
        self.last_order_date = order_date
        self.total_orders += 1
        self.save()

    @classmethod
    def get_active_customers(cls):
        """Get all active customers for Order Service"""
        return cls.objects.filter(status='ACTIVE')

    @classmethod
    def get_customer_for_order(cls, customer_id):
        """Get customer data for Order Service"""
        try:
            customer = cls.objects.get(id=customer_id)
            if not customer.is_active:
                raise ValidationError('Customer is not active')
            return customer.to_dict()
        except cls.DoesNotExist:
            raise ValidationError('Customer not found')

    def validate_for_order(self):
        """Validate customer can place orders"""
        if not self.is_active:
            raise ValidationError('Inactive customers cannot place orders')
        if self.is_blocked:
            raise ValidationError('Blocked customers cannot place orders')
        return True
