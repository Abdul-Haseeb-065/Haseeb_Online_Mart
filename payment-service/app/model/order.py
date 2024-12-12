from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from enum import Enum
from datetime import timezone, datetime, timedelta
from .authentication import BaseIdModel
import uuid


class OrderItemBase(SQLModel):
    product_id: str = Field(foreign_key="product.id")
    product_item_id: str = Field(foreign_key="productitem.id")
    product_size_id: str = Field(foreign_key="productsize.id")
    quantity: int

class OrderPayment(str, Enum):
    cash_on_delivery = "Cash On Delivery" 
    online_payment = "Online Payment"

class OrderDelivery(SQLModel):
    email: str
    country: str
    city: str
    postal_code: str
    address: str
    phone_number: str

class OrderBase(OrderDelivery):
    total_price: float
    order_payment: OrderPayment = Field(default="Cash On Delivery")

class OrderModel(OrderBase):
    items: List[OrderItemBase]

class OrderStatus(str, Enum):
    processing = "Processing"
    shipping = "Shipping"
    delivered = "Delivered"
    cancelled = "Cancelled"


def calculate_delivery_date():
    return datetime.now(timezone.utc) + timedelta(days=7)

class Order(BaseIdModel, OrderBase, table=True):
    tracking_id: Optional[str] = Field(default=uuid.uuid4().hex)
    order_status: Optional[OrderStatus] = Field(default="Processing")
    delivery_date: datetime | None = Field(default_factory=calculate_delivery_date)
    order_date: datetime | None = Field(default=datetime.now(timezone.utc))
    user_id: int = Field(foreign_key="users.id")
    order_items: List["OrderItem"] = Relationship(back_populates="order")


class OrderItem(BaseIdModel, OrderItemBase, table=True):
    order_id: str = Field(foreign_key="order.id") 
    order: Optional["Order"] = Relationship(back_populates="order_items")

class OrderItemDetail(SQLModel):
    product: str
    product_item: dict
    size: str
    price: int
    quantity: int
    stock: int

class OrderDetail(OrderBase):
    order_id: str
    tracking_id: str
    order_status: str
    delivery_date: datetime
    order_date: datetime
    order_items: List[OrderItemDetail]
    user_name: str
    user_email: str
    user_image_url: Optional[str]

class OrderItemMetadata(SQLModel):
    product_id: str
    product_item_id: str
    product_size_id: str
    quantity: int

class OrderMetadata(OrderBase):
    user_id: int
    order_id: str
    items: List[OrderItemMetadata]

##########################################################################################################
class CartItemModel(SQLModel):
    quantity: int = Field(default=1)
    product_item_id: int = Field(default=None, foreign_key="productitem.id")
    product_size_id: int = Field(default=None, foreign_key="productsize.id")

class Cart(BaseIdModel, table=True):
    user_id: int = Field(foreign_key="users.id")
    cart_items: List["CartItem"] = Relationship(back_populates="cart")

class CartItem(CartItemModel, BaseIdModel, table=True):
    cart_id: int = Field(foreign_key="cart.id")
    cart: Optional["Cart"] = Relationship(back_populates="cart_items")

class CartUpdateItem(SQLModel):
    cart_item_id: int
    quantity: int
