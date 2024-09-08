from typing import Optional, List, Literal
from sqlmodel import SQLModel, Field, Relationship


class ProductSize(SQLModel, table=True):
    product_size_id: Optional[int] = Field(None, primary_key=True)
    size_id: int = Field(foreign_key="size.size_id")
    price: int = Field(gt=0)   
    product_item_id: int = Field(foreign_key="productitem.item_id")
    stock: "Stock" = Relationship(back_populates="product_size")
    product_item: Optional["ProductItem"] = Relationship(back_populates="sizes")  
class ProductBase(SQLModel):
    product_name: str 
    product_description: str 
    product_type: str
    duration: str
    gender_id: int = Field(foreign_key="gender.gender_id")
    category_id: int = Field(foreign_key="category.category_id")

class ProductItemBase(SQLModel):
    color: str 

class SizeModel(SQLModel):
    size: int 
    price: int = Field(gt=0) 
    stock: int 

class ProductItemFormModel(ProductItemBase):    
    color: str
    sizes: List[SizeModel] 

class ProductFormModel(ProductBase):
    product_items: List[ProductItemFormModel]


class Product(ProductBase, table=True):
    product_id: Optional[int] = Field(default=None, primary_key=True) 
    product_items: List["ProductItem"] = Relationship(back_populates="product")  
    
class ProductItem(SQLModel, table=True):
    item_id: Optional[int] = Field(default=None, primary_key=True)  
    product_id: int = Field(foreign_key="product.product_id")
    color: str
    product_images: List["ProductImage"] = Relationship( back_populates="product_item") # ref 1
    product: Optional[Product] = Relationship(back_populates="product_items")
    sizes: List[ProductSize] = Relationship(back_populates="product_item")

class ProductImage(SQLModel, table=True):
    product_image_id: Optional[int] = Field(default=None, primary_key=True)
    product_item_id: int = Field(foreign_key="productitem.item_id")
    product_image_url: str
    product_item: Optional["ProductItem"] = Relationship(back_populates="product_images") # ref 1

class Stock(SQLModel, table=True):
    stock_id: Optional[int] = Field(default=None, primary_key=True)
    product_size_id: int = Field(foreign_key="productsize.product_size_id")
    stock: int = 0  
    product_size: Optional[ProductSize] = Relationship(back_populates="stock") 

    @property
    def stock_level(self) -> Literal["Low", "Medium", "High"]:
        if self.stock > 100:
            return "High"
        elif self.stock > 10:
            return "Medium"
        else:
            return "Low"


# Sample JSON payload for creating a product
sample_payload = {
    "product_name": "Shirt",
    "product_description": "New Shirt",
    "product_items": [
        {
            "color": "green",
            "image_url": "http://www.shirt.com",
            "sizes": [
                {
                    "size": "small",
                    "price": 200,
                    "stock": 50
                },
                {
                    "size": "medium",
                    "price": 250,
                    "stock": 10
                },
                {
                    "size": "large",
                    "price": 300,
                    "stock": 0
                }
            ]
        },
    ]
}
