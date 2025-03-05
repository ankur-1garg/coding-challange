from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Order, OrderItem
from .serializers import OrderSerializer
from .permissions import IsSuperUserOrReadOnly, OrderPermission
from rest_framework.permissions import IsAuthenticated
from logging import getLogger

logger = getLogger(__name__)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, OrderPermission]

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                order = self.perform_create(serializer)
                logger.info(f"Order created successfully: {order.id}")
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )

        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return Response(
                {'error': 'Invalid order data', 'details': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            logger.error(f"Order creation failed: {str(e)}")
            return Response(
                {'error': 'Failed to create order'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['POST'])
    def update_status(self, request, pk=None):
        try:
            order = self.get_object()
            new_status = request.data.get('status')

            if new_status not in dict(Order.STATUS_CHOICES):
                return Response(
                    {'error': 'Invalid status value'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            old_status = order.status
            order.status = new_status
            order.save()

            logger.info(
                f"Order {order.id} status updated: {old_status} -> {new_status}"
            )

            return Response({
                'message': 'Status updated successfully',
                'status': new_status
            })

        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            logger.error(f"Status update failed: {str(e)}")
            return Response(
                {'error': 'Failed to update status'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def perform_create(self, serializer):
        return serializer.save(request=self.request)

    def perform_update(self, serializer):
        serializer.save(request=self.request)

    def get_queryset(self):
        """Filter orders based on user permissions"""
        if self.request.user.is_superuser:
            return Order.objects.all()
        return Order.objects.filter(customer_id=self.request.user.id)

    def destroy(self, request, *args, **kwargs):
        return Response(
            {"error": "Orders cannot be deleted"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
