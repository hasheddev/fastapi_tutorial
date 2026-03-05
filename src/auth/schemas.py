from typing import Optional, List
from pydantic import BaseModel, Field
from sqlmodel import Field
import uuid
from datetime import datetime

from src.books import schemas
from src.reviews.schemas import ReviewModel


class UserModel(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    password_hash: str = Field(exclude=True)
    first_name: str
    last_name: str
    role: str
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    def __repr__(self):
        return f"<User {self.username}>"


class UserBookModel(UserModel):
    books: Optional[List["schemas.Book"]]
    reviews: Optional[List[ReviewModel]]


class UserCreate(BaseModel):
    username: str = Field(max_length=12)
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)
    first_name: str = Field(max_length=25)
    last_name: str = Field(max_length=25)


class UserLogin(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)


class EmailModel(BaseModel):
    addresses: list[str]


class SignUpModel(BaseModel):
    user: UserModel
    message: str


class PasswordResetRequestModel(BaseModel):
    email: str


class PasswordResetConfirmModel(BaseModel):
    password: str = Field(min_length=6)
    confrim_password: str = Field(min_length=6)
