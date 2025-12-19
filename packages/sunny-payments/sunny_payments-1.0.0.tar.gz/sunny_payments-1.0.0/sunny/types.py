"""
Sunny Payments SDK - Type Definitions
"""

from typing import TypedDict, Optional, List, Literal, Dict, Any, Union
from typing_extensions import NotRequired


# ============ Common Types ============
Metadata = Dict[str, Union[str, int, bool]]

PaymentStatus = Literal["pending", "processing", "succeeded", "failed", "cancelled", "refunded"]
PaymentSource = Literal["mpesa", "card", "bank_transfer", "wallet", "crypto"]
BillNetwork = Literal["safaricom", "airtel", "telkom"]
BillType = Literal["airtime", "data", "electricity", "utility"]
WebhookEvent = Literal[
    "payment.created",
    "payment.succeeded",
    "payment.failed",
    "payment.refunded",
    "customer.created",
    "customer.updated",
    "customer.deleted",
    "refund.created",
    "refund.succeeded",
    "refund.failed",
]


# ============ Payment Types ============
class PaymentCreateParams(TypedDict):
    amount: int
    currency: str
    source: str
    description: NotRequired[str]
    metadata: NotRequired[Metadata]
    customer: NotRequired[str]
    idempotency_key: NotRequired[str]


class Payment(TypedDict):
    id: str
    amount: int
    currency: str
    status: PaymentStatus
    source: str
    description: NotRequired[str]
    metadata: NotRequired[Metadata]
    customer: NotRequired[str]
    created: str
    captured: NotRequired[bool]
    refunded: NotRequired[bool]


# ============ Customer Types ============
class CustomerCreateParams(TypedDict):
    email: str
    name: NotRequired[str]
    phone: NotRequired[str]
    metadata: NotRequired[Metadata]


class CustomerUpdateParams(TypedDict, total=False):
    email: str
    name: str
    phone: str
    metadata: Metadata


class Customer(TypedDict):
    id: str
    email: str
    name: NotRequired[str]
    phone: NotRequired[str]
    metadata: NotRequired[Metadata]
    created: str


# ============ Refund Types ============
class RefundCreateParams(TypedDict):
    payment: str
    amount: NotRequired[int]
    reason: NotRequired[str]


class Refund(TypedDict):
    id: str
    payment: str
    amount: int
    currency: str
    status: Literal["pending", "succeeded", "failed"]
    reason: NotRequired[str]
    created: str


# ============ Webhook Types ============
class WebhookCreateParams(TypedDict):
    url: str
    events: List[WebhookEvent]
    description: NotRequired[str]
    metadata: NotRequired[Metadata]


class WebhookUpdateParams(TypedDict, total=False):
    url: str
    events: List[WebhookEvent]
    description: str
    status: Literal["active", "disabled"]
    metadata: Metadata


class Webhook(TypedDict):
    id: str
    url: str
    events: List[WebhookEvent]
    description: NotRequired[str]
    status: Literal["active", "disabled"]
    secret: str
    metadata: NotRequired[Metadata]
    created: str


# ============ Bills Types ============
class AirtimePurchaseParams(TypedDict):
    phone_number: str
    amount: int
    network: NotRequired[BillNetwork]


class DataPurchaseParams(TypedDict):
    phone_number: str
    bundle_id: str
    network: NotRequired[BillNetwork]


class ElectricityPurchaseParams(TypedDict):
    meter_number: str
    amount: int
    phone_number: NotRequired[str]
    type: NotRequired[Literal["prepaid", "postpaid"]]


class BillTransaction(TypedDict):
    id: str
    type: BillType
    amount: int
    status: Literal["pending", "succeeded", "failed"]
    reference: NotRequired[str]
    token: NotRequired[str]
    created: str


class DataBundle(TypedDict):
    id: str
    name: str
    amount: int
    data_amount: str
    validity: str
    network: BillNetwork


# ============ Response Types ============
class ListResponse(TypedDict):
    data: List[Any]
    has_more: bool
    total_count: NotRequired[int]
