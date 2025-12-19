"""Custom exceptions for Anzo MCP Server."""

from typing import Dict, Any, Optional


class AnzoAPIError(Exception):
    """Base exception for Anzo API errors."""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.format_message())
    
    def format_message(self) -> str:
        """Format the error message."""
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON serialization."""
        return {
            "error": self.message,
            "status_code": self.status_code,
            "details": self.details
        }


class AnzoConnectionError(AnzoAPIError):
    """Raised when connection to Anzo server fails."""
    pass


class AnzoAuthenticationError(AnzoAPIError):
    """Raised when authentication fails."""
    pass


class AnzoNotFoundError(AnzoAPIError):
    """Raised when requested resource is not found."""
    pass


class AnzoValidationError(AnzoAPIError):
    """Raised when request validation fails."""
    pass


class AnzoTimeoutError(AnzoAPIError):
    """Raised when request times out."""
    pass
