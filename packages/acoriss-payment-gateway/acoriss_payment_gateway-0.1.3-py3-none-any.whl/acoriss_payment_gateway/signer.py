"""Signer interface and implementations."""

import hashlib
import hmac
from abc import ABC, abstractmethod


class SignerInterface(ABC):
    """Abstract base class for signature implementations."""

    @abstractmethod
    def sign(self, data: str) -> str:
        """Sign the given data and return the signature.

        Args:
            data: The data to sign (usually JSON string or payment ID)

        Returns:
            The computed signature as a hex string
        """
        pass


class HmacSha256Signer(SignerInterface):
    """HMAC-SHA256 signature implementation."""

    def __init__(self, secret: str) -> None:
        """Initialize the signer with a secret key.

        Args:
            secret: The secret key for HMAC signing
        """
        self.secret = secret

    def sign(self, data: str) -> str:
        """Sign data using HMAC-SHA256.

        Args:
            data: The data to sign

        Returns:
            The HMAC-SHA256 signature as a hex string
        """
        return hmac.new(
            self.secret.encode("utf-8"),
            data.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
