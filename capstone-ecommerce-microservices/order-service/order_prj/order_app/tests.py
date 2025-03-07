from django.test import TestCase
from test_utils.test_base import BaseTestCase
from rest_framework import status
from .models import Order, OrderItem
from unittest.mock import patch, Mock
import json
from decimal import Decimal
import requests


class OrderAPITests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.customer_id = 'b2e231ee-42c3-43df-bfb8-82af3a7e77c7'
        self.product_id = 'c625c01a-0a12-4438-97b9-c987d7580f72'
        self.valid_order_data = {
            'customer_id': self.customer_id,
            'items': [
                {
                    'product_id': self.product_id,
                    'quantity': 1
                }
            ],
            'status': 'pending'
        }

    @patch('requests.get')
    @patch('requests.patch')
    def test_create_order(self, mock_patch, mock_get):
        # Create proper mock responses
        mock_product_response = Mock()
        mock_product_response.status_code = 200
        mock_product_response.json.return_value = {
            'id': self.product_id,
            'price': '99.99',
            'stock': 10
        }

        mock_customer_response = Mock()
        mock_customer_response.status_code = 200
        mock_customer_response.json.return_value = {
            'id': self.customer_id
        }

        mock_get.side_effect = [mock_product_response, mock_customer_response]

        # Mock patch response for stock update
        mock_stock_response = Mock()
        mock_stock_response.status_code = 200
        mock_stock_response.json.return_value = {'stock': 9}
        mock_patch.return_value = mock_stock_response

        response = self.client.post(
            '/api/orders/', self.valid_order_data, format='json')
        print("Response data:", response.data)  # Debug output

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        created_order = Order.objects.first()
        self.assertEqual(created_order.customer_id, self.customer_id)

    @patch('requests.get')
    def test_insufficient_stock(self, mock_get):
        # Create proper mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': self.product_id,
            'price': '99.99',
            'stock': 0
        }
        mock_get.return_value = mock_response

        response = self.client.post(
            '/api/orders/', self.valid_order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('insufficient stock', str(response.data).lower())

    def test_get_order_list(self):
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('requests.get')
    @patch('requests.patch')
    def test_order_total_price(self, mock_patch, mock_get):
        # Create proper mock responses
        mock_product_response = Mock()
        mock_product_response.status_code = 200
        mock_product_response.json.return_value = {
            'id': self.product_id,
            'price': '99.99',
            'stock': 10
        }

        mock_customer_response = Mock()
        mock_customer_response.status_code = 200
        mock_customer_response.json.return_value = {
            'id': self.customer_id
        }

        mock_get.side_effect = [mock_product_response, mock_customer_response]

        # Mock patch response for stock update
        mock_stock_response = Mock()
        mock_stock_response.status_code = 200
        mock_stock_response.json.return_value = {'stock': 9}
        mock_patch.return_value = mock_stock_response

        response = self.client.post(
            '/api/orders/', self.valid_order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Decimal(response.data['total_price']), Decimal('99.99'))

    @patch('requests.get')
    def test_invalid_customer_id(self, mock_get):
        """Test order creation with non-existent customer"""
        mock_get.side_effect = requests.exceptions.HTTPError(
            "Customer not found")

        invalid_order_data = {
            'customer_id': 'invalid-uuid',
            'items': [{'product_id': self.product_id, 'quantity': 1}],
            'status': 'pending'
        }

        response = self.client.post(
            '/api/orders/', invalid_order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('requests.get')
    def test_invalid_product_id(self, mock_get):
        """Test order creation with non-existent product"""
        mock_get.side_effect = requests.exceptions.HTTPError(
            "Product not found")

        invalid_order_data = {
            'customer_id': self.customer_id,
            'items': [{'product_id': 'invalid-product-id', 'quantity': 1}],
            'status': 'pending'
        }

        response = self.client.post(
            '/api/orders/', invalid_order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('requests.get')
    @patch('requests.patch')
    def test_concurrent_order_creation(self, mock_patch, mock_get):
        """Test handling concurrent orders for same product"""
        mock_product_response = Mock()
        mock_product_response.status_code = 200
        mock_product_response.json.return_value = {
            'id': self.product_id,
            'price': '99.99',
            'stock': 1  # Only 1 item in stock
        }
        mock_get.return_value = mock_product_response

        # Create two concurrent orders
        response1 = self.client.post(
            '/api/orders/', self.valid_order_data, format='json')
        response2 = self.client.post(
            '/api/orders/', self.valid_order_data, format='json')

        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_order_status(self):
        """Test order creation with invalid status"""
        invalid_status_data = {
            'customer_id': self.customer_id,
            'items': [{'product_id': self.product_id, 'quantity': 1}],
            'status': 'invalid_status'
        }

        response = self.client.post(
            '/api/orders/', invalid_status_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('requests.get')
    def test_zero_quantity_order(self, mock_get):
        """Test order creation with zero quantity"""
        zero_quantity_data = {
            'customer_id': self.customer_id,
            'items': [{'product_id': self.product_id, 'quantity': 0}],
            'status': 'pending'
        }

        response = self.client.post(
            '/api/orders/', zero_quantity_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('requests.get')
    @patch('requests.patch')
    def test_service_timeout(self, mock_patch, mock_get):
        """Test handling of service timeouts"""
        mock_get.side_effect = requests.exceptions.Timeout("Service timeout")

        response = self.client.post(
            '/api/orders/', self.valid_order_data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_503_SERVICE_UNAVAILABLE)
