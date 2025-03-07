from django.test import TestCase
from test_utils.test_base import BaseTestCase
from rest_framework import status
from .models import Customer
import uuid


class CustomerAPITests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.valid_customer_data = {
            'email': 'test@example.com',
            'name': 'Test User',
            'phone': '+911234567890',
            'status': 'ACTIVE'
        }

    def test_create_customer(self):
        response = self.client.post(
            '/api/customers/', self.valid_customer_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 1)

    def test_get_customer_list(self):
        # Create test customers
        Customer.objects.create(**self.valid_customer_data)
        response = self.client.get('/api/customers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_customer(self):
        customer = Customer.objects.create(**self.valid_customer_data)
        update_data = {'name': 'Updated Name'}
        response = self.client.patch(
            f'/api/customers/{customer.id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Name')

    def test_invalid_customer_data(self):
        invalid_data = {
            'email': 'invalid-email',
            'name': '',
            'phone': '123'
        }
        response = self.client.post('/api/customers/', invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
