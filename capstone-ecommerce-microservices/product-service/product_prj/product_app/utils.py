import requests
from django.conf import settings
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def check_service_health():
    """Check if all required services are running"""
    services = {
        'customer': settings.CUSTOMER_SERVICE_URL,
        'order': settings.ORDER_SERVICE_URL
    }

    results = {}
    for name, url in services.items():
        try:
            response = requests.get(
                f"{url}/api/health/",
                timeout=settings.SERVICE_HEALTH_CHECK_TIMEOUT
            )
            results[name] = response.status_code == 200
        except requests.RequestException:
            results[name] = False

    return results


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return Response({
            'error': str(exc),
            'service_status': check_service_health()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response
