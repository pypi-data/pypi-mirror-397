"""
Sematryx SDK Exceptions
"""


class SematryxError(Exception):
    """Base exception for Sematryx SDK"""
    
    def __init__(self, message: str, status_code: int | None = None, response: dict | None = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class AuthenticationError(SematryxError):
    """Authentication failed - invalid or missing API key"""
    pass


class RateLimitError(SematryxError):
    """Rate limit exceeded"""
    
    def __init__(self, message: str, retry_after: int | None = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class ValidationError(SematryxError):
    """Request validation failed"""
    
    def __init__(self, message: str, errors: list | None = None, **kwargs):
        super().__init__(message, **kwargs)
        self.errors = errors or []


class OptimizationError(SematryxError):
    """Optimization failed"""
    pass


class ConnectionError(SematryxError):
    """Failed to connect to Sematryx API"""
    pass

