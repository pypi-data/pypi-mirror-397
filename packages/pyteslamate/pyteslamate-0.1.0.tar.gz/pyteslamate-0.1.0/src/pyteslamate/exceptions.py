"""Custom exceptions for TeslaMate API client."""


class TeslamateError(Exception):
    """Base exception for all API client errors."""

    default_message: str = "An unspecified Teslamate error occurred."

    def __init__(self, message: str | None = None) -> None:
        # allow subclasses to provide a default_message class attribute
        self.message = message or self.default_message
        super().__init__(self.message)


class TeslamateAuthenticationError(TeslamateError):
    """Raised when authentication fails (401)."""

    default_message = "Authentication failed"


class TeslamateNotFoundError(TeslamateError):
    """Raised when a resource is not found (404)."""

    default_message = "Resource not found"


class TeslamateRateLimitError(TeslamateError):
    """Raised when rate limit is exceeded (429)."""

    default_message = "Rate limit exceeded"


class TeslamateValidationError(TeslamateError):
    """Raised when request or response validation fails."""

    default_message = "Validation failed"


class TeslamateServerError(TeslamateError):
    """Raised when server returns 5xx error."""

    default_message = "Server error occurred"


class TeslamateTimeoutError(TeslamateError):
    """Raised when a request times out."""

    default_message = "Request timed out"
