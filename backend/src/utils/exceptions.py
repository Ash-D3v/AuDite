"""
Custom Exception Classes
"""

from fastapi import HTTPException
from typing import Any, Dict, Optional

class CustomException(Exception):
    """Base custom exception"""
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(CustomException):
    """Validation error"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 400, details)

class AuthenticationError(CustomException):
    """Authentication error"""
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 401, details)

class AuthorizationError(CustomException):
    """Authorization error"""
    def __init__(self, message: str = "Access denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 403, details)

class NotFoundError(CustomException):
    """Resource not found error"""
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 404, details)

class ConflictError(CustomException):
    """Resource conflict error"""
    def __init__(self, message: str = "Resource conflict", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 409, details)

class RateLimitError(CustomException):
    """Rate limit exceeded error"""
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 429, details)

class MLModelError(CustomException):
    """ML model error"""
    def __init__(self, message: str = "ML model error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 500, details)

class DatabaseError(CustomException):
    """Database error"""
    def __init__(self, message: str = "Database error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 500, details)

def custom_exception_handler(request, exc: CustomException):
    """Custom exception handler"""
    return HTTPException(
        status_code=exc.status_code,
        detail={
            "message": exc.message,
            "details": exc.details
        }
    )
