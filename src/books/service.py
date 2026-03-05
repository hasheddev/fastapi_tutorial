from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from datetime import datetime

from src.db.models import Book
from .schemas import BookCreateModel, BookUpdate


class BookService:
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        return result.all()

    async def get_user_books(self, session: AsyncSession, user_id: str):
        statement = (
            select(Book).where(Book.user_id == user_id).order_by(desc(Book.created_at))
        )
        result = await session.exec(statement)
        return result.all()

    async def get_book_by_id(self, book_id: str, session: AsyncSession):
        statement = select(Book).where(Book.id == book_id)
        result = await session.exec(statement)
        return result.first()

    async def create_book(
        self, user_id: str, book_data: BookCreateModel, session: AsyncSession
    ):
        book_dict = book_data.model_dump()
        new_book = Book(**book_dict)
        new_book.published_date = datetime.strptime(
            book_dict["published_date"], "%Y-%m-%d"
        )
        new_book.user_id = user_id  # type: ignore
        session.add(new_book)
        await session.commit()
        return new_book

    async def update_book(
        self, book_id: str, book_data: BookUpdate, session: AsyncSession
    ):
        book_to_update = await self.get_book_by_id(book_id, session)
        if book_to_update is None:
            return None

        update_dict = book_data.model_dump()
        for k, v in update_dict.items():
            setattr(book_to_update, k, v)
        await session.commit()
        await session.refresh(book_to_update)
        return book_to_update

    async def delete_book(self, book_id: str, session: AsyncSession):
        book_to_delete = await self.get_book_by_id(book_id, session)
        if book_to_delete is None:
            return None
        await session.delete(book_to_delete)
        await session.commit()
        return {}
