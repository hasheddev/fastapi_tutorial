from pydantic import BaseModel, Field
import uuid
from datetime import datetime


class ReviewModel(BaseModel):
    id: uuid.UUID
    text: str
    rating: int = Field(le=5)
    book_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ReviewCreate(BaseModel):
    text: str
    rating: int = Field(le=5)
