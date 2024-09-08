from typing import Optional
from sqlmodel import SQLModel, Field
import uuid

class AdvancePayment(SQLModel):
    advance_payment_method: str
    advance_payment_method_id: str


class PaymentDetails(SQLModel):
    payment_method: Optional[str]
    billing_address: str
    payment_method_id: Optional[str]
    advance_payment: Optional[AdvancePayment]


class Admin(SQLModel, table=True):
    admin_id: int | None = Field(int, primary_key=True)
    admin_name: str
    admin_email: str
    admin_password: str
    admin_kid: str = Field(default=lambda:uuid.uuid4().hex)