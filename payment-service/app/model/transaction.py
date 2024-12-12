from sqlmodel import SQLModel, Field,Relationship, table
from typing import Optional
from enum import Enum
from datetime import datetime
from pydantic import EmailStr
from .authentication import BaseIdModel, Users
from .order import OrderStatus
import uuid

class TransactionModel(SQLModel):
    stripeId: str
    amount: int
    order_id: str = Field(foreign_key="order.id")

class TransactionStatus(str, Enum):
    pending = "Pending"
    completed = "Completed"
    refunded = "Refunded"

class Transaction(BaseIdModel, TransactionModel, table=True):
    transaction_status: Optional[TransactionStatus] = Field(default="Pending")
    user_id: int = Field(foreign_key="users.id")

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.__name__.endswith("Model"):
            cls.__table_args__.update(table=True)


# Transaction Details Class
class TransactionDetail(SQLModel):
    transaction_id: str
    stripeId: str
    amount: int
    order_id: str
    user_id: int
    username: str
    email: str
    imageUrl: str
    order_email: str
    country: str
    city: str
    postal_code: str
    address: str
    phone_number: str
    total_price: float
    order_status: Optional[OrderStatus]
    delivery_date: datetime
    order_date: datetime

class RefundReason(str, Enum):
    duplicate = 'duplicate'
    fraudulent = 'fraudulent'
    requested_by_customer = 'requested_by_customer'

class RefundStatus(str, Enum):
    pending = 'pending'
    requires_action = 'requires_action' 
    succeeded = 'succeeded'
    failed = 'failed'

class RefundModel(SQLModel):
    reason: RefundReason
    amount: float

# Transaction Refund Class
class Refund(BaseIdModel):
    amount: int
    stripeId: str
    refund_id: str
    status: RefundStatus
    reason: RefundReason
    refund_date: datetime = Field(default=datetime.now())
    transaction_id: str = Field(foreign_key="transaction.id")
    user_id: int = Field(foreign_key="users.id")
    order_id: str = Field(foreign_key="order.id")

class RefundDetails(SQLModel):
    refund_id: str
    amount: int
    stripeId: str
    status: RefundStatus
    reason: RefundReason
    refund_date: datetime
    username: str
    email: str
    imageUrl: str
    order_email: str
    country: str
    city: str
    postal_code: str
    address: str
    phone_number: str
    order_status: OrderStatus
    delivery_date: datetime
    order_date: datetime
    user_id: int
    order_id: str
    transaction_id: str