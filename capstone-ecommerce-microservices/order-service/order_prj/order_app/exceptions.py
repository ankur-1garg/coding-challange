class OrderError(Exception):
    """Base class for Order exceptions"""
    pass


class OrderNotFoundError(OrderError):
    """Raised when an order is not found"""
    pass


class InsufficientStockError(OrderError):
    """Raised when there is not enough stock for an order"""
    pass


class ProductNotFoundError(OrderError):
    """Raised when a product does not exist"""
    pass


class DatabaseError(OrderError):
    """Raised when there is a database connection or query error"""
    pass
