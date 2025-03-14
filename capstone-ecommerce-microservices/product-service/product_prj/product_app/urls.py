from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, health_check, validate_token

router = DefaultRouter()
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('health/', health_check, name='health-check'),
    path('validate-token/', validate_token, name='validate-token'),
]
