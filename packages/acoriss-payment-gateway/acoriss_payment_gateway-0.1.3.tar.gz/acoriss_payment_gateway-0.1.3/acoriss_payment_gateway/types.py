"""Type definitions for the Acoriss Payment Gateway SDK."""

from typing import List, Literal, Optional, Protocol, TypedDict

Environment = Literal["sandbox", "live"]
PaymentStatus = Literal["P", "S", "C"]  # P = Pending, S = Succeeded, C = Canceled


class SignerProtocol(Protocol):
    """Protocol for custom signature implementations."""

    def sign(self, data: str) -> str:
        """Sign the given data and return the signature.

        Args:
            data: The data to sign (usually JSON string or payment ID)

        Returns:
            The computed signature as a hex string
        """
        ...


class CustomerInfo(TypedDict, total=False):
    """Customer information for payment session."""

    email: str
    name: str
    phone: Optional[str]


class ServiceItem(TypedDict, total=False):
    """Service item included in payment."""

    name: str
    price: int  # in smallest currency unit (e.g., cents)
    description: Optional[str]
    quantity: Optional[int]  # default 1


class PaymentSessionRequest(TypedDict, total=False):
    """Request payload for creating a payment session."""

    amount: int
    currency: str  # e.g., "USD"
    customer: CustomerInfo
    description: Optional[str]
    callback_url: Optional[str]
    cancel_url: Optional[str]
    success_url: Optional[str]
    transaction_id: Optional[str]  # merchant reference
    service_id: Optional[str] # categorization of the payment
    services: Optional[List[ServiceItem]]


class PaymentSessionResponse(TypedDict):
    """Response from creating a payment session."""

    id: str
    amount: int
    currency: str
    description: Optional[str]
    checkout_url: str
    customer: CustomerInfo
    created_at: str  # ISO date string
    service_id: Optional[str] # categorization of the payment


class PaymentService(TypedDict):
    """Service details in payment response."""

    id: str
    name: str
    description: Optional[str]
    quantity: int
    price: int  # in cents
    currency: Optional[str]  # ISO 4217 or null
    session_id: str
    created_at: str  # ISO date string
    service_id: Optional[str] # categorization of the payment


class RetrievePaymentCustomer(TypedDict):
    """Customer info in retrieve payment response."""

    email: Optional[str]
    phone: Optional[str]


class RetrievePaymentResponse(TypedDict):
    """Response from retrieving a payment."""

    id: str
    amount: int  # in cents
    currency: str  # ISO 4217
    description: Optional[str]
    transaction_id: str
    customer: RetrievePaymentCustomer
    created_at: str  # ISO date string
    expired: bool
    services: List[PaymentService]
    status: PaymentStatus  # 'P' = Pending, 'S' = Succeeded, 'C' = Canceled
    service_id: Optional[str] # categorization of the payment


class ClientConfig(TypedDict, total=False):
    """Configuration for PaymentGatewayClient."""

    api_key: str
    api_secret: Optional[str]
    environment: Optional[Environment]
    base_url: Optional[str]
    signer: Optional[SignerProtocol]
    timeout: Optional[float]
