"""
Authentication for Remote Executor Protocol.

This module implements minimal, explicit authentication for remote execution.
Static token-based authentication only — no OAuth, no sessions, no refresh tokens.

SECURITY PRINCIPLES:
    1. Token must be present
    2. Token must match expected value
    3. Failure rejects execution
    4. Failure returns explicit error
    5. Failure does not leak information

This is intentionally simple. Complex authentication is not the executor's job.
"""

from dataclasses import dataclass
from typing import Optional
import hmac
import hashlib
import time


# =============================================================================
# AUTHENTICATION ERRORS
# =============================================================================


class AuthenticationError(Exception):
    """Base exception for authentication errors."""

    pass


class TokenMissingError(AuthenticationError):
    """Raised when authentication token is missing."""

    def __init__(self) -> None:
        super().__init__("Authentication token is required")


class TokenInvalidError(AuthenticationError):
    """Raised when authentication token is invalid."""

    def __init__(self) -> None:
        # Intentionally vague to prevent information leakage
        super().__init__("Authentication failed")


class TokenExpiredError(AuthenticationError):
    """Raised when request timestamp is too old."""

    def __init__(self) -> None:
        super().__init__("Request expired")


class NonceReusedError(AuthenticationError):
    """Raised when request nonce has been used before."""

    def __init__(self) -> None:
        super().__init__("Request replay detected")


# =============================================================================
# AUTHENTICATION CONFIGURATION
# =============================================================================


@dataclass(frozen=True)
class AuthenticationConfig:
    """
    Configuration for authentication validation.

    Attributes:
        expected_token: The expected authentication token.
        max_request_age_seconds: Maximum age of request timestamp.
        enforce_nonce: Whether to reject reused nonces.
    """

    expected_token: str
    max_request_age_seconds: int = 300  # 5 minutes
    enforce_nonce: bool = True

    def __post_init__(self) -> None:
        """Validate configuration."""
        if not self.expected_token:
            raise ValueError("Expected token cannot be empty")
        if self.max_request_age_seconds < 0:
            raise ValueError("Max request age must be non-negative")


# =============================================================================
# AUTHENTICATION VALIDATOR
# =============================================================================


@dataclass
class AuthenticationValidator:
    """
    Validates authentication for remote execution requests.

    This validator is stateless except for nonce tracking (if enabled).
    It performs constant-time token comparison to prevent timing attacks.

    Attributes:
        config: Authentication configuration.
    """

    config: AuthenticationConfig
    _used_nonces: set = None  # Set of used nonces (if nonce enforcement enabled)

    def __post_init__(self) -> None:
        """Initialize nonce tracking."""
        if self._used_nonces is None:
            self._used_nonces = set()

    def validate(
        self,
        token: str,
        request_timestamp: str,
        request_nonce: str,
    ) -> None:
        """
        Validate authentication credentials.

        Args:
            token: The authentication token from the request.
            request_timestamp: ISO 8601 timestamp from the request.
            request_nonce: Unique nonce from the request.

        Raises:
            TokenMissingError: If token is empty.
            TokenInvalidError: If token does not match.
            TokenExpiredError: If request is too old.
            NonceReusedError: If nonce has been used (and enforcement enabled).
        """
        # Check token is present
        if not token:
            raise TokenMissingError()

        # Constant-time comparison to prevent timing attacks
        if not self._constant_time_compare(token, self.config.expected_token):
            raise TokenInvalidError()

        # Check request age
        if not self._check_timestamp(request_timestamp):
            raise TokenExpiredError()

        # Check nonce uniqueness
        if self.config.enforce_nonce:
            if not self._check_and_record_nonce(request_nonce):
                raise NonceReusedError()

    def _constant_time_compare(self, a: str, b: str) -> bool:
        """
        Constant-time string comparison.

        Prevents timing attacks by always comparing all bytes.

        Args:
            a: First string.
            b: Second string.

        Returns:
            True if strings are equal.
        """
        return hmac.compare_digest(a.encode(), b.encode())

    def _check_timestamp(self, timestamp_str: str) -> bool:
        """
        Check if request timestamp is within acceptable range.

        Args:
            timestamp_str: ISO 8601 timestamp string.

        Returns:
            True if timestamp is within acceptable range.
        """
        try:
            # Parse ISO 8601 timestamp
            from datetime import datetime

            # Handle both with and without Z suffix
            if timestamp_str.endswith("Z"):
                timestamp_str = timestamp_str[:-1]

            request_time = datetime.fromisoformat(timestamp_str)
            current_time = datetime.utcnow()

            # Calculate age in seconds
            age_seconds = abs((current_time - request_time).total_seconds())

            return age_seconds <= self.config.max_request_age_seconds

        except (ValueError, TypeError):
            # Invalid timestamp format
            return False

    def _check_and_record_nonce(self, nonce: str) -> bool:
        """
        Check if nonce is unique and record it.

        Args:
            nonce: The request nonce.

        Returns:
            True if nonce is unique.
        """
        if nonce in self._used_nonces:
            return False

        self._used_nonces.add(nonce)

        # Limit nonce storage to prevent memory exhaustion
        # Keep only the most recent 10000 nonces
        if len(self._used_nonces) > 10000:
            # Remove oldest (this is a simple approach; in production
            # you'd use a time-based eviction strategy)
            self._used_nonces = set(list(self._used_nonces)[-5000:])

        return True

    def clear_nonces(self) -> None:
        """Clear recorded nonces (for testing only)."""
        self._used_nonces.clear()


# =============================================================================
# AUTHENTICATION RESULT
# =============================================================================


@dataclass(frozen=True)
class AuthenticationResult:
    """
    Result of authentication validation.

    Attributes:
        is_valid: True if authentication succeeded.
        error_type: Type of error (if failed).
        error_message: Error message (if failed).
    """

    is_valid: bool
    error_type: Optional[str] = None
    error_message: Optional[str] = None

    @classmethod
    def success(cls) -> "AuthenticationResult":
        """Create a successful authentication result."""
        return cls(is_valid=True)

    @classmethod
    def failure(cls, error: AuthenticationError) -> "AuthenticationResult":
        """Create a failed authentication result."""
        return cls(
            is_valid=False,
            error_type=type(error).__name__,
            error_message=str(error),
        )


def validate_authentication(
    config: AuthenticationConfig,
    token: str,
    request_timestamp: str,
    request_nonce: str,
) -> AuthenticationResult:
    """
    Validate authentication credentials.

    This is a convenience function that creates a validator and validates.

    Args:
        config: Authentication configuration.
        token: The authentication token.
        request_timestamp: ISO 8601 timestamp.
        request_nonce: Unique nonce.

    Returns:
        AuthenticationResult indicating success or failure.
    """
    validator = AuthenticationValidator(config=config)

    try:
        validator.validate(token, request_timestamp, request_nonce)
        return AuthenticationResult.success()
    except AuthenticationError as e:
        return AuthenticationResult.failure(e)


# =============================================================================
# TOKEN GENERATION UTILITIES
# =============================================================================


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token.

    Args:
        length: Length of the token in bytes (output is hex, so 2x characters).

    Returns:
        Hex-encoded random token.
    """
    import secrets

    return secrets.token_hex(length)


def hash_token(token: str) -> str:
    """
    Create a hash of a token for storage/comparison.

    Args:
        token: The token to hash.

    Returns:
        SHA-256 hash of the token.
    """
    return hashlib.sha256(token.encode()).hexdigest()
