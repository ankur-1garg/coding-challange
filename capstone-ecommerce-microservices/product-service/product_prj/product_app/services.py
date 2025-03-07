import requests
from django.conf import settings
from rest_framework import status
from .exceptions import ServiceCommunicationError, TokenValidationError


class ServiceCommunication:
    @staticmethod
    def validate_token_with_customer_service(token):
        """Validate token with customer service"""
        try:
            response = requests.get(
                f"{settings.CUSTOMER_SERVICE_URL}/api/validate-token/",
                headers={'Authorization': f'Token {token}'},
                timeout=settings.SERVICE_TIMEOUT
            )

            if response.status_code == 200:
                return response.json()
            else:
                raise TokenValidationError(
                    f"Token validation failed: {response.status_code}")

        except requests.RequestException as e:
            raise ServiceCommunicationError(
                f"Error communicating with customer service: {str(e)}")

    @staticmethod
    def notify_stock_update(product_id, new_stock, token):
        """Notify order service about stock updates"""
        try:
            response = requests.post(
                f"{settings.ORDER_SERVICE_URL}/api/notify-stock-update/",
                headers={'Authorization': f'Token {token}'},
                json={'product_id': product_id, 'stock': new_stock}
            )
            return response.status_code == status.HTTP_200_OK
        except requests.RequestException as e:
            raise ServiceCommunicationError(
                f"Order service communication error: {str(e)}")
