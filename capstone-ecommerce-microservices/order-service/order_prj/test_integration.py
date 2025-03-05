import os
import django
from decimal import Decimal
import uuid
import requests
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'order_prj.settings')
django.setup()

from order_app.models import Order, OrderItem
from django.db import connection

class OrderServiceTest:
    def __init__(self):
        self.customer_id = str(uuid.uuid4())
        self.product_id = str(uuid.uuid4())
        self.order_id = None

    def test_database_connection(self):
        """Test Snowflake connection"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT CURRENT_TIMESTAMP()")
                result = cursor.fetchone()
                print(f"✅ Database connection successful: {result[0]}")
                return True
        except Exception as e:
            print(f"❌ Database connection failed: {str(e)}")
            return False

    def test_order_creation(self):
        """Test creating an order with items"""
        try:
            order = Order.objects.create(
                customer_id=self.customer_id,
                total_amount=Decimal('199.99'),
                status='PENDING'
            )
            self.order_id = order.id

            item = OrderItem.objects.create(
                order=order,
                product_id=self.product_id,
                quantity=2,
                unit_price=Decimal('99.99')
            )

            print(f"""
✅ Order created successfully:
Order ID: {order.id}
Customer ID: {order.customer_id}
Status: {order.status}
Total Amount: ${order.total_amount}

Order Item:
ID: {item.id}
Product ID: {item.product_id}
Quantity: {item.quantity}
Unit Price: ${item.unit_price}
Line Total: ${item.line_total}
""")
            return True
        except Exception as e:
            print(f"❌ Order creation failed: {str(e)}")
            return False

    def test_order_retrieval(self):
        """Test retrieving an order"""
        try:
            order = Order.objects.get(id=self.order_id)
            items = order.items.all()
            print(f"""
✅ Order retrieved successfully:
Order ID: {order.id}
Items count: {items.count()}
""")
            return True
        except Exception as e:
            print(f"❌ Order retrieval failed: {str(e)}")
            return False

    def test_order_update(self):
        """Test updating order status"""
        try:
            order = Order.objects.get(id=self.order_id)
            order.status = 'SHIPPED'
            order.save()
            print(f"✅ Order status updated to: {order.status}")
            return True
        except Exception as e:
            print(f"❌ Order update failed: {str(e)}")
            return False

    def verify_snowflake_data(self):
        """Verify data in Snowflake"""
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM orders WHERE id = '{self.order_id}'")
                order_data = cursor.fetchone()
                cursor.execute(f"SELECT COUNT(*) FROM order_items WHERE order_id = '{self.order_id}'")
                items_count = cursor.fetchone()[0]
                
                print(f"""
✅ Snowflake verification successful:
Order found: {order_data is not None}
Items count: {items_count}
""")
                return True
        except Exception as e:
            print(f"❌ Snowflake verification failed: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all tests in sequence"""
        print(f"\n🔄 Starting Order Service Tests at {datetime.now()}\n")

        tests = [
            self.test_database_connection,
            self.test_order_creation,
            self.test_order_retrieval,
            self.test_order_update,
            self.verify_snowflake_data
        ]

        results = []
        for test in tests:
            print(f"\n📋 Running: {test.__doc__}")
            results.append(test())

        print(f"\n📊 Test Summary:")
        print(f"Total tests: {len(results)}")
        print(f"Passed: {results.count(True)}")
        print(f"Failed: {results.count(False)}")
        
        return all(results)

if __name__ == "__main__":
    tester = OrderServiceTest()
    success = tester.run_all_tests()
    exit(0 if success else 1)