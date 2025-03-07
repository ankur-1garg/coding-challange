from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
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
        if self.request.user.is_authenticated:
            token, _ = Token.objects.get_or_create(user=self.request.user)
            context['token'] = token.key
        return context

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise ValidationError("Authentication required")
        serializer.save()
