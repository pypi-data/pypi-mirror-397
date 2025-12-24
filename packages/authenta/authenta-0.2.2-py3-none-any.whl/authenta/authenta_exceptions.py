from typing import Literal, Optional, Dict, Any

AuthentaErrorCode = Literal[
    "IAM001", "IAM002",   # Auth
    "AA001", "U007",      # Quota/Billing
    "bad_request", "not_found", "timeout",
    "payload_too_large", "server_error", "unknown",
]


class AuthentaError(Exception):
    """
    Base exception for all Authenta SDK errors.
    """

    def __init__(
        self,
        message: str,
        code: AuthentaErrorCode = "unknown",
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}

        # String repr: "[IAM001] Invalid Key (HTTP 401)"
        text = f"[{code}] {message}"
        if status_code:
            text += f" (HTTP {status_code})"
        super().__init__(text)


class AuthenticationError(AuthentaError):
    """Raised for invalid API keys (Default: IAM001)."""

    def __init__(self, message: str, code: AuthentaErrorCode = "IAM001", **kwargs):
        super().__init__(message, code, **kwargs)


class AuthorizationError(AuthentaError):
    """Raised for permission issues (Default: IAM002)."""

    def __init__(self, message: str, code: AuthentaErrorCode = "IAM002", **kwargs):
        super().__init__(message, code, **kwargs)


class QuotaExceededError(AuthentaError):
    """Raised when rate limits are hit (Default: AA001)."""

    def __init__(self, message: str, code: AuthentaErrorCode = "AA001", **kwargs):
        super().__init__(message, code, **kwargs)


class InsufficientCreditsError(AuthentaError):
    """Raised when account balance is empty (Default: U007)."""

    def __init__(self, message: str, code: AuthentaErrorCode = "U007", **kwargs):
        super().__init__(message, code, **kwargs)


class ValidationError(AuthentaError):
    """Raised for client-side issues (Default: bad_request)."""

    def __init__(self, message: str, code: AuthentaErrorCode = "bad_request", **kwargs):
        super().__init__(message, code, **kwargs)


class ServerError(AuthentaError):
    """Raised for server-side issues (Default: server_error)."""

    def __init__(self, message: str, code: AuthentaErrorCode = "server_error", **kwargs):
        super().__init__(message, code, **kwargs)
