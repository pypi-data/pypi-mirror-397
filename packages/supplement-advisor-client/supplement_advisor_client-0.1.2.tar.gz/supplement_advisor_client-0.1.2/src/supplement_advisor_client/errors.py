"""Custom exceptions for Supplement Advisor API Client."""


class SupplementAdvisorError(Exception):
    """Base exception for all Supplement Advisor API client errors."""
    pass


class APIError(SupplementAdvisorError):
    """Exception raised when API request fails."""
    
    def __init__(self, status_code: int, error_type: str = None, error_message: str = None):
        self.status_code = status_code
        self.error_type = error_type
        self.error_message = error_message
        
        message = f"API request failed with status code {status_code}"
        if error_type:
            message += f", error type: {error_type}"
        if error_message:
            message += f", error message: {error_message}"
        
        super().__init__(message)


class AuthenticationError(APIError):
    """Exception raised when API authentication fails (401/403)."""
    pass


class RateLimitError(APIError):
    """Exception raised when rate limit is exceeded (429)."""
    pass


class ServerError(APIError):
    """Exception raised when server error occurs (5xx)."""
    pass

