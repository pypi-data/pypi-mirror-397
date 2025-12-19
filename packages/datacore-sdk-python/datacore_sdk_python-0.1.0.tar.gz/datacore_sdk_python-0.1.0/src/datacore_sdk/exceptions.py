class DataCoreError(Exception):
    """Base exception for DataCore SDK."""


class APIError(DataCoreError):
    """Represents an HTTP/API error response."""

    def __init__(self, status_code: int, message: str, *, details: dict | None = None):
        super().__init__(f"HTTP {status_code}: {message}")
        self.status_code = status_code
        self.message = message
        self.details = details or {}
