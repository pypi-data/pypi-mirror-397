from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.middleware import (
    AbstractAuthenticationMiddleware,
    AuthenticationResult,
)
import msgspec

from core.storage import Storage

from .services import provide_auth_service, provide_user_service
from .services.auth_service import (
    TOKEN_PREFIX,
    AccountDTO,
    AuthService,
)


class JWTAuthMiddleware(AbstractAuthenticationMiddleware):
    async def authenticate_request(self, connection: ASGIConnection) -> AuthenticationResult:
        auth_header = connection.headers.get("Authorization")
        if not auth_header:
            raise NotAuthorizedException()

        token = auth_header.replace(f"{TOKEN_PREFIX} ", "")
        account_data = AuthService.decode_token(token)
        account = msgspec.convert(account_data, type=AccountDTO)
        await self._check_session(connection, account)

        if not account.id:
            raise NotAuthorizedException()
        return AuthenticationResult(user=account, auth=token)

    @staticmethod
    async def _check_session(connection: ASGIConnection, account: AccountDTO) -> None:
        storage: Storage = await connection.app.dependencies.get("storage")()
        db_session = await connection.app.dependencies.get("db_session")(
            state=connection.app.state,
            scope=connection.scope,
        )
        mail_client = await connection.app.dependencies.get("mail_client")()
        user_service = await provide_user_service(db_session=db_session)
        async for auth_service in provide_auth_service(
            db_session=db_session,
            mail_client=mail_client,
            storage=storage,
            user_service=user_service,
        ):
            await auth_service.check_session(account, connection.headers.get("User-Agent"))
