from typing import Optional
from sqlmodel import SQLModel, Field
import uuid

class UserMain(SQLModel):
    user_name: str
    country: str
    phone_number: int
    address: str = Field()
    zip_code: str | None = Field(max_length=6)

class UserCredentials(SQLModel):
    user_email: str
    user_password: str

class UserBase(UserMain, UserCredentials):
    pass

class User(UserBase, table=True):
    user_id: Optional[int] = Field(primary_key=True)
    is_verified: bool = Field(default=False)
    kid: str = Field(default_factory=lambda: uuid.uuid4().hex)

class UpdatingUser(SQLModel):
    user_name: str | None
    user_email: str | None
    phone_number: int | None
    address: str | None = Field(max_length=60)
    zip_code: str | None = Field(max_length=6)

class SearchHistory():
    user_id: int
    input: list[str]