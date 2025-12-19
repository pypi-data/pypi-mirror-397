import random
from typing import Any, AsyncGenerator
from uuid import UUID, uuid4

import advanced_alchemy
from advanced_alchemy.repository import SQLAlchemyAsyncRepository
import bcrypt
import jwt
from litestar.exceptions import NotAuthorizedException
import msgspec
from nats.js.errors import KeyNotFoundError
from sqlalchemy.ext.asyncio import AsyncSession

from core.mail import MailClient
from core.settings import settings
from core.storage import Storage

from ..models import AuthCodeModel, UserModel
from .user_service import UserService

__all__ = [
    "UserService",
    "AuthService",
    "LoginRequestDTO",
    "LogoutRequestDTO",
    "SignUpRequestDTO",
    "AccountCacheDTO",
    "AccountCacheSessionDTO",
    "provide_auth_service",
    "InvalidPasswordError",
    "InvalidEmailError",
    "DecodeTokenError",
    "UserNotEnabledError",
    "API_KEY_HEADER",
    "TOKEN_PREFIX",
    "AccountDTO",
    "WrongAuthCodeError",
]


API_KEY_HEADER = "Authorization"
TOKEN_PREFIX = "Bearer"


class InvalidPasswordError(Exception):
    pass


class InvalidEmailError(Exception):
    pass


class UserNotEnabledError(Exception):
    pass


class DecodeTokenError(Exception):
    pass


class WrongAuthCodeError(Exception):
    pass


class LoginRequestDTO(msgspec.Struct):
    email: str
    password: str
    device: str


class LogoutRequestDTO(msgspec.Struct):
    user_id: UUID
    session_id: UUID
    device: str


class SignUpRequestDTO(msgspec.Struct):
    email: str
    password: str


class AccountDTO(msgspec.Struct):
    id: UUID
    email: str
    session_id: UUID


class AccountCacheSessionDTO(msgspec.Struct):
    device: str
    session_id: UUID


class AccountCacheDTO(msgspec.Struct):
    id: UUID
    sessions: list[AccountCacheSessionDTO]
    email: str


class LoginResponseDTO(msgspec.Struct):
    user_id: UUID
    token: str
    session_id: UUID


class ActivateUserResponseDTO(msgspec.Struct):
    user_id: UUID
    token: str
    session_id: UUID


class AuthCodeRepository(SQLAlchemyAsyncRepository[AuthCodeModel]):
    model_type = AuthCodeModel


class AuthService:
    def __init__(
        self,
        session: AsyncSession,
        mail_client: MailClient,
        storage: Storage,
        user_service: UserService,
    ):
        self.session = session
        self.mail_client = mail_client
        self.storage = storage
        self.user_service = user_service
        self.auth_code_repository = AuthCodeRepository(session=session)

    async def signup(self, user: SignUpRequestDTO) -> AuthCodeModel:
        signup_user = await self.user_service.create(
            UserModel(
                email=user.email,
                password=self.hash_password(user.password),
                is_email_verified=False,
                is_enabled=False,
            ),
            auto_commit=True,
        )
        auth_code = await self.auth_code_repository.add(
            AuthCodeModel(
                user_id=signup_user.id,
                code=self.generate_activate_code(),
            ),
            auto_commit=True,
        )

        self.mail_client.send([user.email], "Sign up", auth_code.code)
        return auth_code

    async def activate_user(self, code: str, device: str) -> LoginResponseDTO:
        auth_code = await self.auth_code_repository.get_one_or_none(AuthCodeModel.code == code)
        if not auth_code:
            raise WrongAuthCodeError

        user = await self.user_service.update(UserModel(id=auth_code.user_id, is_enabled=True), auto_commit=True)
        return await self._add_account_session(user.id, user.email, device)

    async def login(self, login_data: LoginRequestDTO) -> LoginResponseDTO:
        try:
            login_user = await self.user_service.get_one(UserModel.email == login_data.email)
        except advanced_alchemy.exceptions.NotFoundError:
            raise InvalidEmailError(f"Email {login_data.email} not found")

        if not login_user.is_enabled:
            raise UserNotEnabledError(f"User {login_data.email} not enabled")

        if not self._check_password(login_data.password, login_user.password):
            raise InvalidPasswordError

        return await self._add_account_session(login_user.id, login_user.email, login_data.device)

    async def _add_account_session(self, user_id: UUID, email: str, device: str):
        login_session = AccountCacheSessionDTO(
            session_id=uuid4(),
            device=device,
        )

        try:
            cached_account = await self.storage.get("sessions", str(user_id), model_type=AccountCacheDTO)
            cached_account.sessions.append(login_session)
        except KeyNotFoundError:
            cached_account = AccountCacheDTO(id=user_id, email=email, sessions=[login_session])

        jwt_token = self.encode_token(
            AccountDTO(
                id=user_id,
                email=email,
                session_id=login_session.session_id,
            )
        )
        await self.storage.save("sessions", str(cached_account.id), cached_account)

        return LoginResponseDTO(
            user_id=user_id,
            token=jwt_token,
            session_id=login_session.session_id,
        )

    async def start_reset_password(self, user_id: UUID):
        print("generate reset code")
        print("send reset link to mail")

    async def logout(self, logout_request: LogoutRequestDTO) -> None:
        cached_user = await self.storage.get("sessions", str(logout_request.user_id), model_type=AccountCacheDTO)
        cached_user.sessions = [
            session
            for session in cached_user.sessions
            if not (session.session_id == logout_request.session_id and session.device == logout_request.device)
        ]
        await self.storage.save("sessions", str(logout_request.user_id), cached_user)

    async def check_session(self, account: AccountDTO, device: str):
        try:
            cached_account = await self.storage.get("sessions", str(account.id), model_type=AccountCacheDTO)
            for session in cached_account.sessions:
                if session.session_id == account.session_id:
                    if session.device != device:
                        raise NotAuthorizedException("Wrong device")
                    return
            raise NotAuthorizedException("Session not found")
        except KeyNotFoundError:
            raise NotAuthorizedException()

    @staticmethod
    def _check_password(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt()).decode("utf8")

    async def get_account(self, token: str) -> AccountDTO:
        try:
            account_data = self.decode_token(token)
            return msgspec.convert(account_data, type=AccountDTO)
        except Exception:
            raise DecodeTokenError

    @staticmethod
    def encode_token(account: AccountDTO) -> str:
        return jwt.encode(msgspec.to_builtins(account), settings.jwt_secret, algorithm="HS256")

    @staticmethod
    def decode_token(token: str) -> dict[str, Any]:
        return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])

    @staticmethod
    def generate_activate_code() -> str:
        return "".join(str(random.randint(0, 9)) for _ in range(8))


async def provide_auth_service(
    db_session: AsyncSession,
    mail_client: MailClient,
    storage: Storage,
    user_service: UserService,
) -> AsyncGenerator[AuthService, None]:
    yield AuthService(
        session=db_session,
        mail_client=mail_client,
        storage=storage,
        user_service=user_service,
    )
