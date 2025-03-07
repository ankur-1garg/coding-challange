from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, validate_token, health_check

router = DefaultRouter()
router.register(r'customers', CustomerViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('validate-token/', validate_token, name='validate-token'),
    path('health/', health_check, name='health-check'),
]
