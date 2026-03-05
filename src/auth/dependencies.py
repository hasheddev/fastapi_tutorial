from typing import Any

from fastapi import Request, status, Depends
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.db.redis import check_token_in_block_list
from src.db.models import User
from src.errors import (
    AccountNotVerified,
    InvalidToken,
    InsufficientPermission,
    RevokedToken,
    UserNotFound,
    AccessTokenRequired,
    RefreshTokenRequired,
)
from .service import UserService
from .utils import decode_token

user_service = UserService()


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)
        if creds is None:
            raise InvalidToken()
        token_valid = self.is_token_valid(creds.credentials)
        if not token_valid:
            raise InvalidToken()

        token_data = decode_token(creds.credentials)

        if await check_token_in_block_list(token_data["jti"]):  # type: ignore
            raise RevokedToken()

        self.verify_token_data(token_data)  # type: ignore
        return token_data  # type: ignore

    def is_token_valid(self, token: str) -> bool:
        token_data = decode_token(token)
        return token_data is not None

    def verify_token_data(self, token_data: dict) -> None:
        raise NotImplementedError("Please override this method in child classes")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data["is_refresh"]:
            raise AccessTokenRequired()


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if not token_data["is_refresh"]:
            raise RefreshTokenRequired()


access_token_bearer = AccessTokenBearer()


async def get_current_user(
    token_details: dict = Depends(access_token_bearer),
    session: AsyncSession = Depends(get_session),
):
    user_email: str = token_details["user"]["email"]
    user = await user_service.get_user_by_email(user_email, session)
    if user is None:
        raise UserNotFound()
    return user


class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: User = Depends(get_current_user)) -> Any:
        if current_user.is_verified == False:
            raise AccountNotVerified()
        if current_user.role in self.allowed_roles:
            return True
        raise InsufficientPermission()
