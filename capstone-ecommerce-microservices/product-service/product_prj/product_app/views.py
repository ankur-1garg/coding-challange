from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import DatabaseError, transaction
from .models import Product
from .serializers import ProductSerializer
from .permissions import IsSuperUserOrReadOnly
from logging import getLogger
from .utils import check_service_health
from django.conf import settings
from snowflake.connector.errors import ProgrammingError, DatabaseError as SnowflakeDBError

logger = getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validate_token(request):
    """Endpoint to validate token for product service"""
    return Response({
        'valid': True,
        'user_id': request.user.id,
        'username': request.user.username,
        'is_superuser': request.user.is_superuser,
        'service': 'product-service'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint"""
    return Response({
        'status': 'healthy',
        'service': 'product-service',
        'version': '1.0'
    })


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing products
    GET requests are allowed without authentication
    POST/PUT/DELETE require authentication and superuser status
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self):
        """Override get_object to handle errors"""
        try:
            obj = super().get_object()
            return obj
        except ObjectDoesNotExist:
            return None

    def list(self, request, *args, **kwargs):
        """List all products with proper response handling"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': len(serializer.data),
            'results': serializer.data
        })

    def retrieve(self, request, *args, **kwargs):
        """Get single product with proper response handling"""
        instance = self.get_object()
        if not instance:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_headers_with_token(self, request):
        """Get headers with token for service communication"""
        token = request.auth.key if request.auth else None
        return {
            'Authorization': f'Token {token}',
            'Content-Type': 'application/json'
        } if token else {}

    def create(self, request, *args, **kwargs):
        """Create a new product with error handling and token validation"""
        try:
            if not request.user.is_superuser:
                return Response(
                    {'error': 'Only superusers can create products'},
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                try:
                    with transaction.atomic():
                        self.perform_create(serializer)
                        logger.info(
                            f"Product created by {request.user}: {serializer.data['name']}")
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                except (ProgrammingError, SnowflakeDBError) as e:
                    logger.error(f"Snowflake error: {str(e)}")
                    return Response(
                        {'error': 'Database error', 'details': str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return Response(
                {'error': 'Invalid product data', 'details': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.critical(f"Unexpected error creating product: {str(e)}")
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, *args, **kwargs):
        """Update product with proper response handling"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        if not instance:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['POST'])
    def update_stock(self, request, pk=None):
        """Update product stock (superuser only)"""
        if not request.user.is_superuser:
            return Response(
                {'error': 'Only superusers can update stock'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            product = self.get_object()
            new_stock = request.data.get('stock')

            if new_stock is None:
                return Response(
                    {'error': 'Stock value is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            product.stock = new_stock
            product.save()
            logger.info(
                f"Stock updated by {request.user}: {product.name} -> {new_stock}")

            return Response({'stock': new_stock})
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except DatabaseError as e:
            logger.error(f"Database error during stock update: {str(e)}")
            return Response(
                {'error': 'Database error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.critical(f"Unexpected error during stock update: {str(e)}")
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['GET'])
    def low_stock(self, request):
        """Get products with stock below threshold with error handling"""
        try:
            threshold = int(request.query_params.get('threshold', 10))
            if threshold < 0:
                raise ValueError("Threshold cannot be negative")

            products = self.queryset.filter(stock__lt=threshold)
            serializer = self.get_serializer(products, many=True)

            logger.info(
                f"Low stock query executed: {len(products)} products found")
            return Response({
                'threshold': threshold,
                'count': len(products),
                'products': serializer.data
            })

        except ValueError as e:
            logger.error(f"Invalid threshold value: {str(e)}")
            return Response(
                {'error': 'Invalid threshold value', 'details': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except DatabaseError as e:
            logger.error(f"Database error querying low stock: {str(e)}")
            return Response(
                {'error': 'Database error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.critical(f"Unexpected error in low stock query: {str(e)}")
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
