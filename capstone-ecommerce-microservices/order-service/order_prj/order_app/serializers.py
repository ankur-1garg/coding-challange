from django.conf import settings
import requests
from rest_framework import serializers
from .models import Order, OrderItem
from django.db import transaction
from decimal import Decimal
from .exceptions import ProductServiceError, InsufficientStockError


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product_id', 'quantity']
        extra_kwargs = {
            'product_id': {'required': True},
            'quantity': {'required': True, 'min_value': 1}
        }


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer_id', 'items', 'total_price',
                  'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'total_price', 'created_at', 'updated_at']
        extra_kwargs = {
            'customer_id': {'required': True},
            'status': {'default': 'pending'}
        }

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        token = self.context['request'].auth.key

        with transaction.atomic():
            # Create order with token for customer stats update
            order = Order.objects.create(**validated_data, token=token)

            total_price = Decimal('0.00')

            # Process items
            for item_data in items_data:
                product_data = self._verify_product(item_data, token)
                unit_price = Decimal(str(product_data['price']))
                subtotal = unit_price * item_data['quantity']

                # Create order item
                OrderItem.objects.create(
                    order=order,
                    product_id=item_data['product_id'],
                    quantity=item_data['quantity'],
                    unit_price=unit_price,
                    subtotal=subtotal
                )

                self._update_product_stock(item_data, product_data, token)
                total_price += subtotal

            # Update order total
            order.total_price = total_price
            order.save()
            return order
