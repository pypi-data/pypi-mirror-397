# Acoriss Payment Gateway SDK (Python)

A lightweight Python SDK to create payment sessions with the Acoriss payment gateway.

## Installation

Using pip:

```bash
pip install acoriss-payment-gateway
```

## Quick Start

```python
from acoriss_payment_gateway import PaymentGatewayClient

client = PaymentGatewayClient(
    api_key="your-api-key",
    api_secret="your-api-secret",  # enables automatic HMAC-SHA256 signing
    environment="sandbox",  # or "live"
)

session = client.create_session(
    amount=5000,
    currency="USD",
    customer={
        "email": "john@example.com",
        "name": "John Doe",
        "phone": "+1234567890"
    },
    description="Payment for Order #1234",
    callback_url="https://example.com/api/callback",
    cancel_url="https://example.com/cancel",
    success_url="https://example.com/success",
    transaction_id="order_1234",
    service_id="ecommerce_payment",  # optional: categorize the payment
    services=[
        {
            "name": "express_delivery",
            "price": 1500,
            "description": "Express delivery service",
            "quantity": 1
        }
    ]
)

print("Checkout URL:", session["checkout_url"])
```

### Retrieve Payment Status

```python
payment = client.get_payment("pay_1234567890")

print("Payment Status:", payment["status"])  # 'P' | 'S' | 'C'
print("Amount:", payment["amount"])
print("Expired:", payment["expired"])
print("Services:", payment["services"])
```

Payment status values:
- `'P'` - Pending: Payment is awaiting completion
- `'S'` - Succeeded: Payment was successful
- `'C'` - Canceled: Payment was canceled or failed

## Signature

By default the SDK computes `X-SIGNATURE` as `HMAC-SHA256(body, apiSecret)` if you provide `api_secret`.

If your gateway uses a different signing algorithm, you can:

- Provide a custom signer:

```python
from acoriss_payment_gateway import PaymentGatewayClient
from acoriss_payment_gateway.signer import SignerInterface

class CustomSigner(SignerInterface):
    def sign(self, data: str) -> str:
        return my_custom_signature(data)

client = PaymentGatewayClient(
    api_key="...",
    signer=CustomSigner()
)
```

- Or override per call:

```python
client.create_session(payload, signature_override="precomputed-signature")
```

## Configuration

- `api_key`: str (required)
- `api_secret`: str (optional; enables default HMAC-SHA256 signature)
- `signer`: SignerInterface (optional; custom signer)
- `environment`: "sandbox" | "live" (default: "sandbox")
- `base_url`: str (optional override of base URL)
- `timeout`: float (default: 15.0 seconds)

## API

### Methods

#### `create_session(payload, signature_override=None)`

Creates a new payment session.

**Parameters:**
- `amount`: int - Amount
- `currency`: str - Currency code (e.g., "USD")
- `customer`: dict - Customer info with email, name, and optional phone
- `description`: str (optional) - Payment description
- `callback_url`: str (optional) - Webhook callback URL
- `cancel_url`: str (optional) - Cancel redirect URL
- `success_url`: str (optional) - Success redirect URL
- `transaction_id`: str (optional) - Merchant reference ID
- `service_id`: str (optional) - Service categorization identifier
- `services`: list (optional) - List of service items
- `signature_override`: str (optional) - Custom signature

**Returns:** dict - Session details with checkout URL

#### `get_payment(payment_id, signature_override=None)`

Retrieves payment status and details by payment ID.

**Parameters:**
- `payment_id`: str - The payment ID (e.g., 'pay_1234567890')
- `signature_override`: str (optional) - Custom signature

**Returns:** dict - Payment details including status, services, and customer info

## Error Handling

Errors raise `APIError` with `status`, `data`, and `headers` from the HTTP response when available.

```python
from acoriss_payment_gateway.errors import APIError

try:
    session = client.create_session(...)
except APIError as e:
    print(f"Status: {e.status}")
    print(f"Message: {e.message}")
    print(f"Data: {e.data}")
```

## Development

```bash
# Install dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run tests with coverage
pytest --cov=acoriss_payment_gateway --cov-report=html

# Type checking
mypy acoriss_payment_gateway

# Linting
ruff check acoriss_payment_gateway
```

## License

MIT
