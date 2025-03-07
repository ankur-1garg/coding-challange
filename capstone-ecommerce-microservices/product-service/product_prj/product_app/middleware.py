from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
import requests


class TokenValidationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'api' in request.path and not request.path.endswith('health/'):
            auth_header = request.META.get('HTTP_AUTHORIZATION')
            if auth_header and auth_header.startswith('Token '):
                token = auth_header.split(' ')[1]
                try:
                    # Validate token with customer service
                    response = requests.get(
                        f"{settings.CUSTOMER_SERVICE_URL}/api/validate-token/",
                        headers={'Authorization': f'Token {token}'},
                        timeout=5
                    )
                    if response.status_code != 200:
                        return Response(
                            {'error': 'Invalid token'},
                            status=status.HTTP_401_UNAUTHORIZED
                        )
                except requests.RequestException:
                    pass  # Continue if customer service is unavailable

        return self.get_response(request)
