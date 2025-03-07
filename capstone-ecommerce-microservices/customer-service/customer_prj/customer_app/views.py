from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.exceptions import ValidationError
from django.db import DatabaseError, transaction
from .models import Customer
from .serializers import CustomerSerializer
from .permissions import IsSuperUserOrReadOnly
from logging import getLogger
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

logger = getLogger(__name__)


class CustomerViewSet(viewsets.ModelViewSet):
    """ViewSet for managing customers with role-based permissions"""
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsSuperUserOrReadOnly]

    def perform_create(self, serializer):
        """Log creation with user info"""
        instance = serializer.save()
        logger.info(
            f"Customer created by {self.request.user}: {instance.email}")

    def perform_update(self, serializer):
        """Log updates with user info"""
        instance = serializer.save()
        logger.info(
            f"Customer updated by {self.request.user}: {instance.email}")

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                logger.info(
                    f"Customer created by {request.user.username}: {serializer.data['email']}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            logger.error(
                f"Validation error by {request.user.username}: {str(e)}")
            return Response(
                {'error': 'Invalid customer data', 'details': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except DatabaseError as e:
            logger.error(
                f"Database error by {request.user.username}: {str(e)}")
            return Response(
                {'error': 'Database error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            logger.info(f"Customer updated successfully: {instance.id}")
            return Response(serializer.data)
        except Customer.DoesNotExist:
            logger.warning(f"Customer not found: {kwargs.get('pk')}")
            return Response(
                {'error': 'Customer not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return Response(
                {'error': 'Invalid customer data', 'details': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['POST'])
    def change_status(self, request, pk=None):
        """Change customer status (superuser only)"""
        if not request.user.is_superuser:
            return Response(
                {'error': 'Only superusers can change status'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            customer = self.get_object()
            new_status = request.data.get('status')

            if new_status not in dict(Customer.STATUS_CHOICES):
                return Response(
                    {'error': 'Invalid status value'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            customer.change_status(new_status)
            logger.info(
                f"Status changed by {request.user}: {customer.email} -> {new_status}")

            return Response({'status': new_status})
        except Customer.DoesNotExist:
            return Response(
                {'error': 'Customer not found'},
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def validate_token(request):
    """Endpoint to validate token and return user info"""
    return Response({
        'user': {
            'id': request.user.id,
            'email': request.user.email,
            'is_superuser': request.user.is_superuser
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_auth_token(request):
    """Generate or retrieve authentication token"""
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({
            'error': 'Both username and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'is_superuser': user.is_superuser
        })

    return Response({
        'error': 'Invalid credentials'
    }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validate_token(request):
    """Endpoint to validate token"""
    return Response({
        'valid': True,
        'user_id': request.user.id,
        'username': request.user.username,
        'is_superuser': request.user.is_superuser
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint that doesn't require authentication"""
    return Response({
        'status': 'healthy',
        'service': 'customer-service',
        'version': '1.0'
    })
