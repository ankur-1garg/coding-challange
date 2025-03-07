from django.conf import settings
import requests
from rest_framework import serializers
from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'customer_id', 'product_id', 'quantity',
                  'total_price', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'total_price', 'created_at', 'updated_at']
        extra_kwargs = {
            'status': {'default': 'pending'},
            'customer_id': {'required': True},
            'product_id': {'required': True},
            'quantity': {'required': True}
        }

    def create(self, validated_data):
        token = self.context.get('request').auth.key
        order = Order(**validated_data)
        order.save(token=token)
        return order
