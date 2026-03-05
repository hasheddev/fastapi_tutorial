from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import timedelta, datetime

from src.celery_tasks import send_email
from src.db.main import get_session
from src.db.redis import add_jti_to_blocklist
from src.config import Config
from src.mail import create_message, mail
from .dependencies import (
    AccessTokenBearer,
    RefreshTokenBearer,
    RoleChecker,
    get_current_user,
)
from .schemas import (
    EmailModel,
    PasswordResetRequestModel,
    PasswordResetConfirmModel,
    SignUpModel,
    UserBookModel,
    UserCreate,
    UserModel,
    UserLogin,
)
from .service import UserService
from .utils import (
    create_access_token,
    create_url_safe_token,
    decode_url_safe_token,
    verify_password,
    generate_passord_hash,
)
from src.errors import InvalidToken, UserExists, InvalidCredentials, UserNotFound

REFRESH_EXPIRY_DATE = 2

access_token_bearer = AccessTokenBearer()
refresh_token_bearer = RefreshTokenBearer()
role_checker = RoleChecker(allowed_roles=["admin", "user"])

auth_router = APIRouter()
user_service = UserService()


@auth_router.post(
    "/signup", response_model=SignUpModel, status_code=status.HTTP_201_CREATED
)
async def create_user_account(
    user_data: UserCreate, session: AsyncSession = Depends(get_session)
):
    user = await user_service.create_user(user_data, session)
    if user is None:
        raise UserExists()
    token = create_url_safe_token({"email": user.email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"
    html = f"""
<h1>Verify your Email</hi>
<p>Please click this <a href="{link}">link</a> to verify your email</p>"""
    emails = [user.email]
    send_email.delay(emails, "Verify your account", html)  # type: ignore
    return {
        "user": user,
        "message": "Account created! Check your email to verify your account",
    }


@auth_router.post("/login", response_model=UserModel, status_code=status.HTTP_200_OK)
async def login_user(
    user_data: UserLogin, session: AsyncSession = Depends(get_session)
):
    email = user_data.email
    password = user_data.password
    user = await user_service.get_user_by_email(email, session)
    if user is None:
        raise InvalidCredentials()
    is_valid = verify_password(password, user.password_hash)
    if not is_valid:
        raise InvalidCredentials()
    user_dict = {"email": user.email, "id": str(user.id), "role": user.role}
    access_token = create_access_token(user_data=user_dict)
    refresh_token = create_access_token(
        user_data=user_dict, is_refresh=True, expiry=timedelta(days=REFRESH_EXPIRY_DATE)
    )
    return JSONResponse(
        content={
            "message": "Login successfull",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user_dict,
        }
    )


@auth_router.get("/refresh_token", status_code=status.HTTP_200_OK)
async def get_new_access_token(token_details=Depends(refresh_token_bearer)):
    expiry_timestamp = token_details["exp"]
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_details["user"])
        return JSONResponse(content={"access_token": new_access_token})

    raise InvalidToken()


@auth_router.get("/me", response_model=UserBookModel, status_code=status.HTTP_200_OK)
async def get_user_info(
    user: UserBookModel = Depends(get_current_user),
    _: bool = Depends(role_checker),
):
    return user


@auth_router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    token_details=Depends(access_token_bearer), _: bool = Depends(role_checker)
):
    jti = token_details["jti"]
    await add_jti_to_blocklist(jti)
    return JSONResponse(content={"message": "Logged out successfully"})


@auth_router.post("/send_mail")
async def send_mail(email: EmailModel):
    emails = email.addresses
    html = """<h1>Welcome to the app</h1>"""
    send_email.delay(emails, "Welcome", html)  # type: ignore
    return {"message": "Email sent successfully"}


@auth_router.get("/verify/{token}")
async def verify_email(token: str, session: AsyncSession = Depends(get_session)):
    token_data = decode_url_safe_token(token)
    if token_data is None:
        raise InvalidToken()
    email = token_data.get("email")
    if email is None:
        raise InvalidToken()
    user_data = {"is_verified": True}
    user = await user_service.update_user(email, user_data, session)
    if user is None:
        return JSONResponse(
            content={"message": "Account verification failed"},
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return JSONResponse(
        content={"message": "Account verified successfuly"},
        status_code=status.HTTP_200_OK,
    )


@auth_router.post("/password-reset-req")
async def request_password_reset(email_data: PasswordResetRequestModel):
    email = email_data.email
    token = create_url_safe_token({"email": email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"
    html = f"""
<h1>Reset your Password</hi>
<p>Please click this <a href="{link}">link</a> to Reset your password</p>"""
    emails = [email]
    send_email.delay(emails, "Reset your password", html)  # type: ignore
    return JSONResponse(
        content={
            "message": "please check your rmail for instructiions to reset your password",
        },
        status_code=status.HTTP_200_OK,
    )


@auth_router.post("/password-reset-confirm/{token}")
async def confirm_password_reset(
    token: str,
    passwords: PasswordResetConfirmModel,
    session: AsyncSession = Depends(get_session),
):
    if passwords.password != passwords.confrim_password:
        raise HTTPException(
            detail="Passwords do not match", status_code=status.HTTP_400_BAD_REQUEST
        )
    token_data = decode_url_safe_token(token)
    if token_data is None:
        raise InvalidToken()
    email = token_data.get("email")
    if email is None:
        raise InvalidToken()
    hash = generate_passord_hash(passwords.password)
    user_data = {"password_hash": hash}
    user = await user_service.update_user(email, user_data, session)
    if user is None:
        return JSONResponse(
            content={"message": "Password update failed"},
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return JSONResponse(
        content={"message": "Password changed successfully!"},
        status_code=status.HTTP_200_OK,
    )
