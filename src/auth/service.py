from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from src.db.models import User
from src.errors import UserNotFound
from .schemas import UserCreate
from .utils import generate_passord_hash, verify_password


class UserService:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)
        result = await session.exec(statement)
        user = result.first()
        return user

    async def user_exists(self, email: str, session: AsyncSession):
        user = await self.get_user_by_email(email, session)
        return user is not None

    async def create_user(self, user_data: UserCreate, session: AsyncSession):
        user_exists = await self.user_exists(user_data.email, session)
        if user_exists:
            return None
        user_dict = user_data.model_dump()
        new_user = User(**user_dict)
        new_user.role = "user"
        new_user.password_hash = generate_passord_hash(user_dict["password"])
        session.add(new_user)
        await session.commit()
        return new_user

    async def update_user(self, email: str, user_data: dict, session: AsyncSession):
        user: User | None = await self.get_user_by_email(email, session)
        if user is None:
            return None
        for k, v in user_data.items():
            setattr(user, k, v)
        await session.commit()
        await session.refresh(user)
        return user
