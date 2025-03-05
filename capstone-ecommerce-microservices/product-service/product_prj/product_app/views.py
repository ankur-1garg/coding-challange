from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.exceptions import ValidationError
from django.db import DatabaseError, transaction
from .models import Product
from .serializers import ProductSerializer
from .permissions import IsSuperUserOrReadOnly
from logging import getLogger

logger = getLogger(__name__)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing products with role-based permissions.
    Provides CRUD operations and custom actions.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsSuperUserOrReadOnly]

    def create(self, request, *args, **kwargs):
        """Create a new product with error handling"""
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                logger.info(
                    f"Product created by {request.user}: {serializer.data['name']}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return Response(
                {'error': 'Invalid product data', 'details': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except DatabaseError as e:
            logger.error(f"Database error: {str(e)}")
            return Response(
                {'error': 'Database error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.critical(f"Unexpected error creating product: {str(e)}")
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, *args, **kwargs):
        """Update a product with error handling"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            logger.info(f"Product updated successfully: {instance.id}")
            return Response(serializer.data)
        except Product.DoesNotExist as e:
            logger.warning(f"Product not found: {kwargs.get('pk')}")
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            logger.error(f"Validation error updating product: {str(e)}")
            return Response(
                {'error': 'Invalid product data', 'details': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.critical(f"Unexpected error updating product: {str(e)}")
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
