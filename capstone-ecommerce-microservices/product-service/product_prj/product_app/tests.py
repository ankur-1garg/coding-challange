from django.test import TestCase
from test_utils.test_base import BaseTestCase
from rest_framework import status
from .models import Product
from decimal import Decimal


class ProductAPITests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.valid_product_data = {
            'name': 'Test Product',
            'price': '99.99',
            'stock': 10
        }

    def test_create_product(self):
        response = self.client.post('/api/products/', self.valid_product_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)

    def test_update_stock(self):
        product = Product.objects.create(**self.valid_product_data)
        response = self.client.patch(
            f'/api/products/{product.id}/',
            {'stock': 5}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['stock'], 5)

    def test_negative_stock(self):
        response = self.client.post('/api/products/', {
            **self.valid_product_data,
            'stock': -1
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_price(self):
        response = self.client.post('/api/products/', {
            **self.valid_product_data,
            'price': '-10.00'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
