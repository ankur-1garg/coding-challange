from rest_framework import authentication
from rest_framework import exceptions
import requests
from django.conf import settings


class CustomerTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None

        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            raise exceptions.AuthenticationFailed('Invalid token header')

        # Try customer service first
        customer_response = requests.get(
            f"{settings.CUSTOMER_SERVICE_URL}/api/validate-token/",
            headers={'Authorization': f'Token {token}'}
        )

        if customer_response.status_code == 200:
            user_data = customer_response.json()
            return (user_data['user'], token)

        # Try product service next
        product_response = requests.get(
            f"{settings.PRODUCT_SERVICE_URL}/api/validate-token/",
            headers={'Authorization': f'Token {token}'}
        )

        if product_response.status_code == 200:
            user_data = product_response.json()
            return (user_data['user'], token)

        raise exceptions.AuthenticationFailed('Invalid token')
