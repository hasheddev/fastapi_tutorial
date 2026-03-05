from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import RoleChecker, get_current_user, User
from src.db.main import get_session
from .schemas import ReviewCreate
from .service import ReviewService

review_router = APIRouter()
review_service = ReviewService()
admin_role_checker = Depends(RoleChecker(["admin"]))
user_role_checker = Depends(RoleChecker(["user", "admin"]))


@review_router.post("/{book_id}")
async def add_review_to_book(
    book_id: str,
    review_data: ReviewCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    new_review = await review_service.add_book_review(
        session, book_id, user.email, review_data
    )
    return new_review


@review_router.get("/{review_id}", dependencies=[user_role_checker])
async def get_review(review_id: str, session: AsyncSession = Depends(get_session)):
    review = await review_service.get_review(review_id, session)

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )
    return review


@review_router.delete(
    "/{review_id}",
    dependencies=[user_role_checker],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_review(
    review_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await review_service.delete_review_from_book(
        review_id=review_id, user_email=current_user.email, session=session
    )

    return None
