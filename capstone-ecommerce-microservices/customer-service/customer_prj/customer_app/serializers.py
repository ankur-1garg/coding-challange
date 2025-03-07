from rest_framework import serializers
from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'email', 'name', 'phone', 'status',
                  'created_at', 'updated_at', 'last_order_date', 'total_orders']
        read_only_fields = ['id', 'created_at', 'updated_at']
