from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, validate_token, health_check

router = DefaultRouter()
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('validate-token/', validate_token, name='validate-token'),
    path('health/', health_check, name='health-check'),
]
