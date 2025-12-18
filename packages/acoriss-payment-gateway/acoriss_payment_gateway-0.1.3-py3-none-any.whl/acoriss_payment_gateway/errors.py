"""Error classes for the Acoriss Payment Gateway SDK."""

from typing import Any, Dict, Optional


class APIError(Exception):
    """Exception raised when API requests fail."""

    def __init__(
        self,
        message: str,
        status: Optional[int] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """Initialize APIError.

        Args:
            message: Error message
            status: HTTP status code
            data: Response data
            headers: Response headers
        """
        super().__init__(message)
        self.message = message
        self.status = status
        self.data = data
        self.headers = headers

    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.status:
            return f"APIError({self.status}): {self.message}"
        return f"APIError: {self.message}"

    def __repr__(self) -> str:
        """Return detailed representation of the error."""
        return (
            f"APIError(message={self.message!r}, status={self.status!r}, data={self.data!r}, headers={self.headers!r})"
        )
