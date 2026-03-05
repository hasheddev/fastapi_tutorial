from typing import Any, Callable, Awaitable
from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse


class BooklyException(Exception):
    """This is the base error class for all bookely errors"""

    pass


class InvalidToken(BooklyException):
    """User has provided an invalid token or no token"""

    pass


class RevokedToken(BooklyException):
    """User has provided a revoked token"""

    pass


class AccessTokenRequired(BooklyException):
    """User has provided a refresh token in place of an access token"""

    pass


class RefreshTokenRequired(BooklyException):
    """User has provided an access token in place of an refresh token"""

    pass


class InvalidCredentials(BooklyException):
    """User has provided an invalid login or signup credentials"""

    pass


class UserExists(BooklyException):
    """User has provided an email for an existing user during signup"""

    pass


class InsufficientPermission(BooklyException):
    """User does not have the necessary permissions to perform an action"""

    pass


class UserNotFound(BooklyException):
    """User requested for not found"""

    pass


class AccountNotVerified(BooklyException):
    """Account not yet verified"""

    pass


class BookNotFound(BooklyException):
    """Book requested for not found"""

    pass


class TagNotFound(BooklyException):
    """Tag requested for not found"""

    pass


class TagAlreadyExists(BooklyException):
    """Tag to create already exists"""

    pass


class InternalServerError(BooklyException):
    """Error due to server"""

    pass


def create_exception_handler(
    status_code: int, detail: Any
) -> Callable[[Request, Exception], Awaitable[JSONResponse]]:
    async def exception_handler(request: Request, exception: Exception) -> JSONResponse:
        return JSONResponse(content=detail, status_code=status_code)

    return exception_handler


def register_errors(app: FastAPI):
    app.add_exception_handler(
        UserExists,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "User with email already exists",
                "error_code": "user_exists",
            },
        ),
    )

    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "User not found", "error_code": "user_not_found"},
        ),
    )
    app.add_exception_handler(
        BookNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Book not found", "error_code": "book_not_found"},
        ),
    )

    app.add_exception_handler(
        TagNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Tag not found", "error_code": "tag_not_found"},
        ),
    )

    app.add_exception_handler(
        InternalServerError,
        create_exception_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Oops! something went wrong",
                "error_code": "internal_server_error",
            },
        ),
    )

    app.add_exception_handler(
        InsufficientPermission,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "You do not have the permission to perform this act",
                "error_code": "insufficient_permission",
            },
        ),
    )

    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "Invalid email or password",
                "error_code": "invalid_credentials",
            },
        ),
    )

    app.add_exception_handler(
        TagAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Tag already exists",
                "error_code": "tag_exists",
            },
        ),
    )

    app.add_exception_handler(
        RevokedToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "Revoked token provided",
                "error_code": "revoked_token",
            },
        ),
    )

    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "No token or invalid token provided",
                "error_code": "invalid_token",
            },
        ),
    )

    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "Please provide an access token",
                "error_code": "access_token_required",
            },
        ),
    )

    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "Please provie a refresh token",
                "error_code": "refresh_token_required",
            },
        ),
    )

    app.add_exception_handler(
        AccountNotVerified,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Account not verified",
                "error_code": "account_notverified",
            },
        ),
    )

    @app.exception_handler(500)
    async def internal_error_handler(req: Request, exc: Exception):
        return JSONResponse(
            content={
                "message": "Oops! something went wrong",
                "error_code": "internal_server_error",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
