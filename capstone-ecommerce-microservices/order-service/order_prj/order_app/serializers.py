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

    def validate(self, attrs):
        headers = {'Authorization': f'Token {self.context.get("token")}'}
        try:
            # Fetch product details
            response = requests.get(
                f"{settings.PRODUCT_SERVICE_URL}/product/products/{attrs['product_id']}/",
                headers=headers,
                timeout=5
            )
            response.raise_for_status()
            product_data = response.json()

            # Check if product has enough stock
            if product_data['stock'] < attrs['quantity']:
                raise serializers.ValidationError(
                    f"Insufficient stock. Available: {product_data['stock']}, Requested: {attrs['quantity']}"
                )

            attrs['unit_price'] = Decimal(str(product_data['price']))
            attrs['current_stock'] = product_data['stock']
            return attrs
        except requests.RequestException as e:
            raise serializers.ValidationError(
                f"Error fetching product: {str(e)}")


class OrderItemReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product_id', 'quantity', 'unit_price']
        read_only_fields = ['unit_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, write_only=True)
    order_items = OrderItemReadSerializer(
        many=True, read_only=True, source='items')
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer_id', 'items', 'order_items', 'status',
                  'total_price', 'created_at', 'updated_at']
        read_only_fields = ['id', 'total_price',
                            'created_at', 'updated_at', 'order_items']

    def create(self, validated_data):
        token = self.context.get('token')
        items_data = validated_data.pop('items', [])
        headers = {'Authorization': f'Token {token}'} if token else {}

        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            total_price = Decimal('0.00')

            # Create order items and update stock
            for item_data in items_data:
                # Create order item
                item = OrderItem.objects.create(
                    order=order,
                    product_id=item_data['product_id'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price']
                )
                total_price += item.unit_price * item.quantity

                # Update product stock
                try:
                    new_stock = item_data['current_stock'] - \
                        item_data['quantity']
                    response = requests.patch(
                        f"{settings.PRODUCT_SERVICE_URL}/product/products/{item_data['product_id']}/",
                        headers=headers,
                        json={'stock': new_stock},
                        timeout=5
                    )
                    response.raise_for_status()
                except requests.RequestException as e:
                    # Rollback the entire transaction if stock update fails
                    raise serializers.ValidationError(
                        f"Failed to update product stock: {str(e)}"
                    )

            # Update order total price
            order.total_price = total_price
            order.save()

            if token:
                order.update_customer_statistics(token)

            return order
