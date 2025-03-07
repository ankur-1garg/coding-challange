from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
import requests
from .models import Order
from .serializers import OrderSerializer
from .exceptions import OrderNotFoundError, ProductNotFoundError, InsufficientStockError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)

# Add this new function


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint that doesn't require authentication"""
    return Response({
        'status': 'healthy',
        'service': 'order-service',
        'version': '1.0'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validate_token(request):
    """Endpoint to validate token for order service"""
    return Response({
        'valid': True,
        'user_id': request.user.id,
    })


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['token'] = self.request.auth.key if self.request.auth else None
        return context

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Order creation failed: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
