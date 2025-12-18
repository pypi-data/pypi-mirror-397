"""Main client for the Acoriss Payment Gateway SDK."""

import json
from typing import Any, Dict, Optional

import requests
from requests.exceptions import RequestException

from acoriss_payment_gateway.errors import APIError
from acoriss_payment_gateway.signer import HmacSha256Signer, SignerInterface
from acoriss_payment_gateway.types import (
    Environment,
    PaymentSessionResponse,
    RetrievePaymentResponse,
)

BASE_URLS: Dict[Environment, str] = {
    "sandbox": "https://sandbox.checkout.rdcard.net/api/v1",
    "live": "https://checkout.rdcard.net/api/v1",
}


class PaymentGatewayClient:
    """Client for interacting with the Acoriss Payment Gateway API."""

    def __init__(
        self,
        api_key: str,
        api_secret: Optional[str] = None,
        environment: Environment = "sandbox",
        base_url: Optional[str] = None,
        signer: Optional[SignerInterface] = None,
        timeout: float = 15.0,
    ) -> None:
        """Initialize the Payment Gateway client.

        Args:
            api_key: API key for authentication
            api_secret: Optional API secret for HMAC-SHA256 signing
            environment: Environment to use ("sandbox" or "live")
            base_url: Optional override for base URL (ignores environment if provided)
            signer: Optional custom signer implementation
            timeout: Request timeout in seconds (default: 15.0)

        Raises:
            ValueError: If neither api_secret nor signer is provided
        """
        self.api_key = api_key
        self.base_url = base_url or BASE_URLS[environment]
        self.timeout = timeout

        # Set up signer
        if signer:
            self.signer: Optional[SignerInterface] = signer
        elif api_secret:
            self.signer = HmacSha256Signer(api_secret)
        else:
            self.signer = None

    def create_session(
        self,
        amount: int,
        currency: str,
        customer: Dict[str, Any],
        description: Optional[str] = None,
        callback_url: Optional[str] = None,
        cancel_url: Optional[str] = None,
        success_url: Optional[str] = None,
        transaction_id: Optional[str] = None,
        services: Optional[list] = None,
        service_id: Optional[str] = None,
        signature_override: Optional[str] = None,
        **extra: Any,
    ) -> PaymentSessionResponse:
        """Create a payment session.

        Args:
            amount: Amount
            currency: Currency code (e.g., "USD")
            customer: Customer information dict with email, name, and optional phone
            description: Optional payment description
            callback_url: Optional webhook callback URL
            cancel_url: Optional cancel redirect URL
            success_url: Optional success redirect URL
            transaction_id: Optional merchant reference ID
            services: Optional list of service items
            service_id: Optional categorization of the payment
            signature_override: Optional pre-computed signature
            **extra: Additional fields for forward compatibility

        Returns:
            Payment session response with checkout URL

        Raises:
            APIError: If the request fails
            ValueError: If no signature is available
        """
        payload: Dict[str, Any] = {
            "amount": amount,
            "currency": currency,
            "customer": customer,
            "serviceId": service_id,
        }

        if description is not None:
            payload["description"] = description
        if callback_url is not None:
            payload["callbackUrl"] = callback_url
        if cancel_url is not None:
            payload["cancelUrl"] = cancel_url
        if success_url is not None:
            payload["successUrl"] = success_url
        if transaction_id is not None:
            payload["transactionId"] = transaction_id
        if services is not None:
            payload["services"] = services
        if service_id is not None:
            payload["serviceId"] = service_id

        # Add any extra fields
        payload.update(extra)

        raw_body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
        signature = signature_override or (self.signer.sign(raw_body) if self.signer else None)

        if not signature:
            raise ValueError(
                "No signature available. Provide api_secret at client init, "
                "a custom signer, or pass signature_override."
            )

        headers = {
            "Content-Type": "application/json",
            "X-API-KEY": self.api_key,
            "X-SIGNATURE": signature,
        }

        try:
            response = requests.post(
                f"{self.base_url}/sessions",
                data=raw_body,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()

            # Convert snake_case to camelCase for consistency with API
            return self._convert_keys_to_snake_case(data)  # type: ignore
        except RequestException as e:
            self._raise_api_error(e)
            raise  # This line is unreachable but makes mypy happy

    def get_payment(
        self,
        payment_id: str,
        signature_override: Optional[str] = None,
    ) -> RetrievePaymentResponse:
        """Retrieve a payment by ID.

        Args:
            payment_id: The payment ID (e.g., 'pay_1234567890')
            signature_override: Optional pre-computed signature

        Returns:
            Payment details including status, services, and customer info

        Raises:
            APIError: If the request fails
            ValueError: If no signature is available
        """
        signature = signature_override or (self.signer.sign(payment_id) if self.signer else None)

        if not signature:
            raise ValueError(
                "No signature available. Provide api_secret at client init, "
                "a custom signer, or pass signature_override."
            )

        headers = {
            "X-API-KEY": self.api_key,
            "X-SIGNATURE": signature,
        }

        try:
            response = requests.get(
                f"{self.base_url}/sessions/{payment_id}",
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()

            # Convert camelCase to snake_case
            return self._convert_keys_to_snake_case(data)  # type: ignore
        except RequestException as e:
            self._raise_api_error(e)
            raise  # This line is unreachable but makes mypy happy

    def _convert_keys_to_snake_case(self, obj: Any) -> Any:
        """Convert camelCase keys to snake_case recursively."""
        if isinstance(obj, dict):
            return {self._to_snake_case(k): self._convert_keys_to_snake_case(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_keys_to_snake_case(item) for item in obj]
        return obj

    @staticmethod
    def _to_snake_case(camel_str: str) -> str:
        """Convert camelCase string to snake_case."""
        result = []
        for i, char in enumerate(camel_str):
            if char.isupper() and i > 0:
                result.append("_")
                result.append(char.lower())
            else:
                result.append(char.lower())
        return "".join(result)

    def _raise_api_error(self, exc: RequestException) -> None:
        """Convert a requests exception to an APIError and raise it.

        Args:
            exc: The requests exception to convert

        Raises:
            APIError: Always raises
        """
        if exc.response is not None:
            try:
                data = exc.response.json()
                message = data.get("message", str(exc))
            except (ValueError, KeyError):
                data = exc.response.text
                message = str(exc)

            raise APIError(
                message=message,
                status=exc.response.status_code,
                data=data,
                headers=dict(exc.response.headers),
            ) from exc
        else:
            raise APIError(message=str(exc)) from exc
