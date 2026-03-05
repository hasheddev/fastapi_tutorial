from typing import Optional, List
import uuid
from pydantic import BaseModel
from datetime import date, datetime

from src.reviews.schemas import ReviewModel


class Book(BaseModel):
    id: uuid.UUID
    title: str
    page_count: int
    author: str
    language: str
    publisher: str
    user_id: Optional[uuid.UUID]
    published_date: date
    created_at: datetime
    updated_at: datetime


class BookReview(Book):
    reviews: List[ReviewModel]


class BookCreateModel(BaseModel):
    title: str
    page_count: int
    author: str
    language: str
    publisher: str
    published_date: str


class BookUpdate(BaseModel):
    title: str
    page_count: int
    author: str
    language: str
    publisher: str
