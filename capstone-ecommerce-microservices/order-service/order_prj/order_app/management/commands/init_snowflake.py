from django.core.management.base import BaseCommand
from django.db import connection
import logging

class Command(BaseCommand):
    help = 'Initialize Snowflake tables for Order service'

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            try:
                # Set context
                self.stdout.write("Setting up Snowflake context...")
                cursor.execute("USE WAREHOUSE COMPUTE_WH")
                cursor.execute("USE DATABASE TRIAL_DB")
                cursor.execute("USE SCHEMA TRIAL_SCMA")

                # Drop existing tables if they exist
                self.stdout.write("Dropping existing tables...")
                cursor.execute("DROP TABLE IF EXISTS order_items")
                cursor.execute("DROP TABLE IF EXISTS orders")

                # Create orders table
                self.stdout.write("Creating orders table...")
                cursor.execute("""
                    CREATE TABLE orders (
                        id VARCHAR(36) PRIMARY KEY,
                        customer_id VARCHAR(36) NOT NULL,
                        total_amount NUMBER(10,2),
                        status VARCHAR(50) DEFAULT 'PENDING',
                        created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                        updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
                    )
                """)

                # Create order_items table
                self.stdout.write("Creating order_items table...")
                cursor.execute("""
                    CREATE TABLE order_items (
                        id VARCHAR(36) PRIMARY KEY,
                        order_id VARCHAR(36),
                        product_id VARCHAR(36) NOT NULL,
                        quantity INTEGER,
                        unit_price NUMBER(10,2),
                        line_total NUMBER(10,2),
                        FOREIGN KEY (order_id) REFERENCES orders(id)
                    )
                """)

                self.stdout.write(self.style.SUCCESS('Successfully created Snowflake tables'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
                raise