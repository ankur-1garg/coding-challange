import requests
from django.conf import settings
from rest_framework.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

class ServiceIntegration:
    @staticmethod
    def verify_customer(customer_id):
        """Verify customer exists in Customer service"""
        service_settings = settings.MICROSERVICE_SETTINGS['CUSTOMER_SERVICE']
        
        try:
            response = requests.get(
                f"{service_settings['URL']}/api/customers/{customer_id}/",
                headers={'Authorization': f"Token {service_settings['TOKEN']}"},
                timeout=service_settings['TIMEOUT']
            )
            
            if response.status_code == 404:
                raise ValidationError("Customer not found")
            elif response.status_code != 200:
                raise ValidationError("Customer verification failed")
                
            customer_data = response.json()
            if customer_data.get('status') != 'ACTIVE':
                raise ValidationError("Customer account is not active")
                
            return True
            
        except requests.RequestException as e:
            logger.error(f"Customer service error: {str(e)}")
            raise ValidationError("Unable to verify customer")

    @staticmethod
    def verify_product(product_id, quantity):
        """Verify product exists and has sufficient stock"""
        service_settings = settings.MICROSERVICE_SETTINGS['PRODUCT_SERVICE']
        
        try:
            response = requests.get(
                f"{service_settings['URL']}/api/products/{product_id}/",
                headers={'Authorization': f"Token {service_settings['TOKEN']}"},
                timeout=service_settings['TIMEOUT']
            )
            
            if response.status_code == 404:
                raise ValidationError("Product not found")
            elif response.status_code != 200:
                raise ValidationError("Product verification failed")
                
            product_data = response.json()
            if product_data['stock'] < quantity:
                raise ValidationError(f"Insufficient stock. Available: {product_data['stock']}")
                
            return product_data
            
        except requests.RequestException as e:
            logger.error(f"Product service error: {str(e)}")
            raise ValidationError("Unable to verify product")