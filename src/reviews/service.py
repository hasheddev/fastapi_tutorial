from fastapi.exceptions import HTTPException
from fastapi import status
from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.service import UserService
from src.books.service import BookService
from src.db.models import Review
from src.reviews.schemas import ReviewCreate
from src.errors import BookNotFound, InternalServerError, UserNotFound

book_service = BookService()
user_service = UserService()


class ReviewService:
    async def add_book_review(
        self,
        session: AsyncSession,
        book_id: str,
        user_email: str,
        review_data: ReviewCreate,
    ):
        try:
            book = await book_service.get_book_by_id(book_id, session)
            if book is None:
                raise BookNotFound()
            user = await user_service.get_user_by_email(user_email, session)
            if user is None:
                raise UserNotFound()
            new_review = Review(**review_data.model_dump())
            new_review.user = user
            new_review.book = book
            session.add(new_review)
            await session.commit()
            return new_review

        except (BookNotFound, UserNotFound) as e:
            raise e

        except Exception as e:
            raise InternalServerError()

    async def get_review(self, id: str, session: AsyncSession):
        statement = select(Review).where(Review.id == id)

        result = await session.exec(statement)

        return result.first()

    async def get_all_reviews(self, session: AsyncSession):
        statement = select(Review).order_by(desc(Review.created_at))

        result = await session.exec(statement)

        return result.all()

    async def delete_review_from_book(
        self, review_id: str, user_email: str, session: AsyncSession
    ):
        user = await user_service.get_user_by_email(user_email, session)
        if user is None:
            raise HTTPException(
                detail="User not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        review = await self.get_review(review_id, session)

        if not review or (review.user != user):
            raise HTTPException(
                detail="Cannot delete this review",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        await session.delete(review)

        await session.commit()
