class OrderError(Exception):
    """Base class for Order exceptions"""
    pass


class OrderNotFoundError(OrderError):
    """Raised when an order is not found"""
    pass


class InsufficientStockError(Exception):
    """Exception raised when there is insufficient stock for an order"""
    pass


class ProductNotFoundError(Exception):
    """Exception raised when a product cannot be found"""
    pass


class DatabaseError(OrderError):
    """Raised when there is a database connection or query error"""
    pass


class ProductServiceError(Exception):
    """Exception raised when there is an error communicating with the product service"""
    pass


class OrderValidationError(Exception):
    """Exception raised when order validation fails"""
    pass
