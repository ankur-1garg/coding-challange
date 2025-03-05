from rest_framework import serializers
from rest_framework.serializers import ValidationError
from .models import Order, OrderItem
from .utils import ServiceIntegration
import requests
from django.conf import settings
from django.db import transaction


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product_id', 'quantity', 'unit_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer_id', 'status', 'total_amount',
            'created_at', 'created_by', 'updated_by', 'items'  # Added 'items' here
        ]
        read_only_fields = [
            'id', 'created_at', 'total_amount',
            'created_by', 'updated_by'
        ]

    def validate(self, data):
        # Verify customer exists and is active
        ServiceIntegration.verify_customer(data['customer_id'])

        # Verify all products exist and have sufficient stock
        for item in data['items']:
            product_data = ServiceIntegration.verify_product(
                item['product_id'],
                item['quantity']
            )
            item['unit_price'] = product_data['price']

        return data

    def create(self, validated_data):
        with transaction.atomic():
            items_data = validated_data.pop('items')
            # Calculate total amount from verified prices
            total_amount = sum(
                item['quantity'] * item['unit_price']
                for item in items_data
            )
            validated_data['total_amount'] = total_amount

            order = Order.objects.create(**validated_data)

            # Create order items
            for item_data in items_data:
                OrderItem.objects.create(order=order, **item_data)

            # Update product stock in Product service
            for item in items_data:
                try:
                    ServiceIntegration.update_product_stock(
                        item['product_id'],
                        item['quantity'],
                        'decrease'
                    )
                except Exception as e:
                    # If stock update fails, rollback the entire order
                    raise ValidationError(
                        f"Failed to update product stock: {str(e)}")

            return order
