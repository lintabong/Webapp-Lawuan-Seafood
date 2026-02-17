

class ServiceError(Exception):
    """Base service exception"""
    pass


class ValidationError(ServiceError):
    """Raised when input validation fails"""
    pass


class NotFoundError(ServiceError):
    """Raised when data not found"""
    pass
