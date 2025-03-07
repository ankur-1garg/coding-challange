import snowflake.connector
from django.conf import settings
from .exceptions import DatabaseError


def get_snowflake_connection():
    """Establish a connection to Snowflake."""
    try:
        conn = snowflake.connector.connect(
            user=settings.SNOWFLAKE_USER,
            password=settings.SNOWFLAKE_PASSWORD,
            account=settings.SNOWFLAKE_ACCOUNT,
            database=settings.SNOWFLAKE_DATABASE,
            schema=settings.SNOWFLAKE_SCHEMA
        )
        return conn
    except Exception as e:
        raise DatabaseError(f"Snowflake Connection Error: {str(e)}")
