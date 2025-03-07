from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Initialize Snowflake database schema'

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            # Create the products table if it doesn't exist
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS PRODUCTS (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                price NUMBER(10,2) NOT NULL,
                stock INTEGER DEFAULT 0,
                created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
            )
            """)

            # Create indexes
            cursor.execute("""
            CREATE INDEX IF NOT EXISTS products_name_idx ON PRODUCTS(name)
            """)

            self.stdout.write(self.style.SUCCESS(
                'Successfully initialized database schema'))
