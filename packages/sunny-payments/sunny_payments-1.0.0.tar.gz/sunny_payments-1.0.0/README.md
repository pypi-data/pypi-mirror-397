# Sunny Payments Python SDK

The official Python SDK for [Sunny Payments](https://sunnypayments.com) - Payment processing made simple.

[![PyPI version](https://img.shields.io/pypi/v/sunny-payments.svg)](https://pypi.org/project/sunny-payments/)
[![Python versions](https://img.shields.io/pypi/pyversions/sunny-payments.svg)](https://pypi.org/project/sunny-payments/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install sunny-payments
```

## Quick Start

```python
from sunny import Sunny

# Initialize the client with your API key
sunny = Sunny("sk_live_your_api_key")

# Create a payment
payment = sunny.payments.create(
    amount=1000,
    currency="KES",
    source="mpesa",
    description="Order #12345"
)

print(payment["id"])  # pay_xxxxx
```

## Features

- ✅ **Payments** - Create, capture, refund, and manage payments
- ✅ **Customers** - Create and manage customer profiles
- ✅ **Refunds** - Process full and partial refunds
- ✅ **Webhooks** - Register endpoints and verify signatures
- ✅ **Bills** - Airtime, data, electricity, and utility payments
- ✅ **Type Hints** - Full type annotations included

## Usage Examples

### Payments

```python
# Create a payment
payment = sunny.payments.create(
    amount=5000,
    currency="KES",
    source="mpesa",
    metadata={"order_id": "12345"}
)

# Retrieve a payment
payment = sunny.payments.retrieve("pay_123")

# List payments
result = sunny.payments.list(limit=10)
for payment in result["data"]:
    print(payment["id"])

# Refund a payment
sunny.payments.refund("pay_123", amount=2500, reason="Customer request")
```

### Bill Payments

```python
# Purchase airtime
airtime = sunny.bills.purchase_airtime(
    phone_number="+254712345678",
    amount=100,
    network="safaricom"
)

# Get data bundles
bundles = sunny.bills.get_data_bundles("safaricom")

# Buy electricity tokens
electricity = sunny.bills.purchase_electricity(
    meter_number="12345678",
    amount=500,
    phone_number="+254712345678"
)
print(electricity["token"])  # KPLC token
```

### Webhooks

```python
from flask import Flask, request
from sunny.resources.webhooks import WebhooksResource

app = Flask(__name__)
WEBHOOK_SECRET = "whsec_xxx"

@app.route("/webhooks/sunny", methods=["POST"])
def handle_webhook():
    payload = request.data
    signature = request.headers.get("x-sunny-signature")
    
    if not WebhooksResource.verify_signature(payload, signature, WEBHOOK_SECRET):
        return "Invalid signature", 400
    
    event = request.json
    
    if event["type"] == "payment.succeeded":
        # Handle successful payment
        pass
    
    return "OK", 200
```

## Error Handling

```python
from sunny import Sunny, AuthenticationError, ValidationError, RateLimitError

try:
    payment = sunny.payments.create(...)
except AuthenticationError:
    print("Invalid API key")
except ValidationError as e:
    print(f"Validation error: {e.message}, field: {e.field}")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
```

## License

MIT License - see [LICENSE](LICENSE) for details.
