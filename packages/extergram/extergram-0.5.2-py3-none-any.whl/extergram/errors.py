# extergram/errors.py

class ExtergramError(Exception):
    """Base exception class for the Extergram library."""
    pass

class APIError(ExtergramError):
    """Raised when the Telegram API returns an error."""
    def __init__(self, description: str, error_code: int):
        self.description = description
        self.error_code = error_code
        super().__init__(f"[Error {error_code}] {description}")

class NetworkError(APIError):
    """Raised when a network-related error occurs (e.g., connection timeout)."""
    pass

class BadRequestError(APIError):
    """Raised for 400 Bad Request errors. Often indicates a problem with the request parameters."""
    pass

class UnauthorizedError(APIError):
    """Raised for 401 Unauthorized errors. Typically means the bot token is invalid."""
    pass

class ForbiddenError(APIError):
    """Raised for 403 Forbidden errors. The bot was blocked by the user or is not a member of the chat."""
    pass

class NotFoundError(APIError):
    """Raised for 404 Not Found errors. The requested resource could not be found."""
    pass