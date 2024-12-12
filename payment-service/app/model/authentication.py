from sqlmodel import SQLModel, Field,Relationship
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
import random as r
import uuid

class BaseIdModel(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime | None = Field(default_factory=datetime.now)
    updated_at: datetime | None = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.now}
    )

class UserBase(BaseIdModel):
    kid: Optional[str] = Field(default=uuid.uuid4().hex)
    username: str = Field(index=True)
    email: str = Field(index=True)
    hashed_password: Optional[str] = Field(default=None, index=True)
    imageUrl: Optional[str] = Field(default=None)
    is_active: Optional[bool] = Field(default=True)
    is_verified: Optional[bool] = Field(default=False)
    otp: Optional[str] = Field(default=None, index=True)

class UserGender(str,Enum):
    male = "male"
    female = "female"
    other = "other"

# User Model
class UserModel(SQLModel):
    username: str
    email: str
    hashed_password: str
    phone_number: str
    imageUrl: Optional[str] = Field(default=None)
    date_of_birth: Optional[str]
    gender: Optional[UserGender]


# Users Model
class Users(UserBase, table=True):
    date_of_birth: Optional[str]
    gender: Optional[UserGender]
    phone_number: Optional[str] = Field(default=None, index=True)
    role: Optional[str] = Field(default="user")

# Admin Model
class Admin(UserBase, BaseIdModel, table=True):
    role: str = Field(default="admin")

class Token(SQLModel):
    access_token: str
    token_type: str
    access_expires_in: int
    refresh_token: str
    refresh_token_expires_in: int

class TokenData(BaseModel):
    username: str | None = None
    email: str | None = None

