import uuid
from sqlmodel import Field, SQLModel
from typing import Optional


class Admin(SQLModel, table=True):
    admin_id: int | None = Field(int, primary_key=True)
    admin_name: str
    admin_email: str
    admin_password: str
    admin_kid: str = Field(default=lambda: uuid.uuid4().hex)



class Category(SQLModel, table=True):
    category_id: Optional[int] = Field(None, primary_key=True)
    category_name: str


class Gender(SQLModel, table=True):
    gender_id: Optional[int] = Field(None, primary_key=True)
    gender_name: str
   

class Size(SQLModel, table=True):
    size_id: Optional[int] = Field(primary_key=True)
    size: str  # Size of the product (e.g., S, M, L)