from fastapi import HTTPException, APIRouter, status, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import AccessTokenBearer, RoleChecker
from src.books.schemas import Book, BookReview, BookUpdate, BookCreateModel
from src.books.service import BookService
from src.db.models import Book as BookModel
from src.db.main import get_session
from src.errors import BookNotFound


book_router = APIRouter()
book_service = BookService()

access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(["admin", "user"]))


def error_on_missing_book(book_id: str, book: BookModel | None):
    if book is None:
        raise BookNotFound()
    return book


@book_router.get("/", response_model=list[Book], dependencies=[role_checker])
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(access_token_bearer),
):
    books = await book_service.get_all_books(session)
    return books


@book_router.get(
    "/user/{user_id}", response_model=list[Book], dependencies=[role_checker]
)
async def get_user_books(
    user_id: str,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(access_token_bearer),
):
    books = await book_service.get_user_books(session, user_id)
    return books


@book_router.get("/{book_id}", response_model=BookReview, dependencies=[role_checker])
async def get_book(
    book_id: str,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(access_token_bearer),
):
    book = await book_service.get_book_by_id(book_id, session)
    return error_on_missing_book(book_id, book)


@book_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=Book,
    dependencies=[role_checker],
)
async def create_book(
    book_data: BookCreateModel,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    user_id = token_details["user"]["id"]
    new_book = await book_service.create_book(user_id, book_data, session)
    return new_book


@book_router.patch("/{book_id}", response_model=Book, dependencies=[role_checker])
async def update_book(
    book_id: str,
    book_data: BookUpdate,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(access_token_bearer),
):
    book = await book_service.update_book(book_id, book_data, session)
    return error_on_missing_book(book_id, book)


@book_router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[role_checker],
)
async def delete_book(
    book_id: str,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(access_token_bearer),
):
    book = await book_service.delete_book(book_id, session)
    if book is None:
        raise BookNotFound()
    return {}
