from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from .views import CustomerViewSet, validate_token, health_check

router = DefaultRouter()
router.register(r'customers', CustomerViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('validate-token/', validate_token, name='validate-token'),
    path('health/', health_check, name='health-check'),
    path('api-auth/', include('rest_framework.urls')),  # Add this line
    path('api-token-auth/', views.obtain_auth_token),  # Add this line
]
