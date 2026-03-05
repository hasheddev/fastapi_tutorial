from typing import Optional
from sqlmodel import SQLModel, Field, Column, Relationship
from datetime import datetime, date
import sqlalchemy.dialects.postgresql as pg
import uuid
from typing import List


class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore

    id: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    username: str
    email: str
    password_hash: str = Field(exclude=True)
    first_name: str
    last_name: str
    role: str = Field(sa_column=Column(pg.VARCHAR, server_default="user"))
    is_verified: bool = Field(default=False)
    books: List["Book"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )
    reviews: List["Review"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    )

    def __repr__(self):
        return f"<User {self.username}>"


class Review(SQLModel, table=True):
    __tablename__ = "reviews"  # type: ignore

    id: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    text: str
    rating: int = Field(le=5, description="The rating must be less than 6")
    book_id: uuid.UUID = Field(foreign_key="books.id")
    user_id: uuid.UUID = Field(foreign_key="users.id")
    user: "User" = Relationship(back_populates="reviews")
    book: "Book" = Relationship(back_populates="reviews")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    )

    def __repr__(self):
        return f"<Review by {self.user_id} for {self.book_id}>"


class BookTag(SQLModel, table=True):
    book_id: uuid.UUID = Field(foreign_key="books.id", primary_key=True)
    tag_id: uuid.UUID = Field(foreign_key="tags.id", primary_key=True)


class Book(SQLModel, table=True):
    __tablename__ = "books"  # type: ignore

    id: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    title: str
    page_count: int
    author: str
    language: str
    publisher: str
    published_date: date
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")
    user: Optional["User"] = Relationship(back_populates="books")
    reviews: List["Review"] = Relationship(
        back_populates="book", sa_relationship_kwargs={"lazy": "selectin"}
    )
    tags: List["Tag"] = Relationship(
        link_model=BookTag,
        back_populates="books",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    )

    def __repr__(self):
        return f"<Book {self.title}>"


class Tag(SQLModel, table=True):
    __tablename__ = "tags"  # type: ignore
    id: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    name: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    books: List["Book"] = Relationship(
        link_model=BookTag,
        back_populates="tags",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    def __repr__(self) -> str:
        return f"<Tag {self.name}>"
