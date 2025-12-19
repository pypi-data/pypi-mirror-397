from typing import Any
from uuid import UUID

from litestar import Controller, Request, get, post
from litestar.datastructures import State
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_400_BAD_REQUEST
import msgspec

from auth.services import (
    AuthService,
    LoginRequestDTO,
    LogoutRequestDTO,
    SignUpRequestDTO,
    UserNotEnabledError,
    provide_auth_service,
    provide_user_service,
)


class Account(msgspec.Struct):
    id: UUID
    session_id: UUID
    email: str


class SignUpRequestScheme(msgspec.Struct):
    email: str
    password: str


class SignUpResponseScheme(msgspec.Struct):
    message: str


class LoginResponseScheme(msgspec.Struct):
    token: str
    id: UUID


class ActivateAccountResponseScheme(msgspec.Struct):
    token: str
    id: UUID


class LoginRequestScheme(msgspec.Struct):
    email: str
    password: str


class ActivateAccountRequestScheme(msgspec.Struct):
    code: str


class AccountController(Controller):
    path = "/account"

    dependencies = {
        "user_service": Provide(provide_user_service),
        "auth_service": Provide(provide_auth_service),
    }

    @get("/")
    async def account(self, request: Request[Account, Any, State]) -> Account:
        return request.user

    @post("/login", exclude_from_auth=True)
    async def login(self, request: Request, data: LoginRequestScheme, auth_service: AuthService) -> LoginResponseScheme:
        device = request.headers.get("User-Agent")

        try:
            login_user = await auth_service.login(
                LoginRequestDTO(
                    email=data.email,
                    password=data.password,
                    device=device,
                )
            )
        except UserNotEnabledError:
            raise HTTPException(f"User {data.email} is not enabled", status_code=HTTP_400_BAD_REQUEST)
        return LoginResponseScheme(token=login_user.token, id=login_user.user_id)

    @post("/signup", exclude_from_auth=True)
    async def sign_up(self, data: SignUpRequestScheme, auth_service: AuthService) -> SignUpResponseScheme:
        await auth_service.signup(SignUpRequestDTO(email=data.email, password=data.password))
        return SignUpResponseScheme(message="success")

    @post("/logout")
    async def logout(self, auth_service: AuthService, request: Request[Account, Any, State]) -> None:
        await auth_service.logout(
            LogoutRequestDTO(
                user_id=request.user.id,
                session_id=request.user.session_id,
                device=request.headers.get("User-Agent"),
            )
        )

    @post("/activate", exclude_from_auth=True)
    async def activate(
        self,
        data: ActivateAccountRequestScheme,
        auth_service: AuthService,
        request: Request,
    ) -> ActivateAccountResponseScheme:
        device = request.headers.get("User-Agent")
        activated_user = await auth_service.activate_user(data.code, device)
        return ActivateAccountResponseScheme(token=activated_user.token, id=activated_user.user_id)
