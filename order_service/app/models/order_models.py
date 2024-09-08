from datetime import datetime, timezone
from typing import List, Literal, Optional
import uuid
from sqlmodel import Field, Relationship, SQLModel


class OrderItemBase(SQLModel):
    product_id: int = Field(foreign_key="product.product_id")
    product_item_id: int = Field(foreign_key="productitem.item_id")
    product_size_id: int = Field(foreign_key="productsize.product_size_id")
    quantity: int


class OrderBase(SQLModel):
    user_id: int = Field(foreign_key="user.user_id")
    order_address: str = Field(max_length=60)


class OrderModel(OrderBase):
    items: List[OrderItemBase]


class Order(OrderBase, table=True):
    order_id: Optional[int] = Field(default=None, primary_key=True)
    total_price: float
    advance_price: Optional[float]
    order_type: str
    order_status: str = Field(default="pending")
    order_date: datetime = Field(default=datetime.now(timezone.utc))

    items: List["OrderItem"] = Relationship(back_populates="order")



class OrderItem(OrderItemBase, table=True):
    order_item_id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.order_id")
    order: Optional[Order] = Relationship(back_populates="items")


class ProductSize(SQLModel, table=True):
    product_size_id: Optional[int] = Field(None, primary_key=True)
    size_id: int = Field(foreign_key="size.size_id")
    price: int = Field(gt=0)
    product_item_id: int= Field(foreign_key="productitem.item_id")
    stock: "Stock" = Relationship(back_populates="product_size")
    product_item: Optional["ProductItem"] = Relationship(back_populates="sizes") 


class Product(SQLModel, table=True):
    product_id: Optional[int] = Field(default=None, primary_key=True)
    product_name: str  
    product_description: str  
    product_type: str
    duration: str
    advance_payment_percentage: float = Field(default=0)
    gender_id: int = Field(foreign_key="gender.gender_id")
    category_id: int = Field(foreign_key="category.category_id")
    product_items: List["ProductItem"] = Relationship( back_populates="product")  


class ProductItem(SQLModel, table=True):
    item_id: Optional[int] = Field( default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.product_id")
    color: str
    product_images: List["ProductImage"] = Relationship( back_populates="product_item")
    product: Optional[Product] = Relationship(back_populates="product_items")
    sizes: List[ProductSize] = Relationship(back_populates="product_item")

class ProductImage(SQLModel, table=True):
    product_image_id: Optional[int] = Field(default=None, primary_key=True)
    product_item_id: int = Field(foreign_key="productitem.item_id")
    product_image_url: str
    product_item: Optional[ProductItem] = Relationship(back_populates="product_images")


class Stock(SQLModel, table=True):
    stock_id: Optional[int] = Field(default=None, primary_key=True)  
    product_size_id: int = Field(foreign_key="productsize.product_size_id")
    stock: int = 0 
    product_size: Optional[ProductSize] = Relationship(back_populates="stock") 

    @property
    def stock_level(self) -> Literal["Low", "Medium", "High"]:
        if self.stock > 100:
            return "High"
        elif self.stock > 50:
            return "Medium"
        else:
            return "Low"


class User(SQLModel, table=True):
    user_id: Optional[int] = Field(int, primary_key=True)
    user_name: str
    user_email: str
    user_password: str
    country: str
    address: str = Field(max_length=60)
    phone_number: int
    is_verified: bool = Field(default=False)
    kid: str = Field(default=lambda: uuid.uuid4().hex)
