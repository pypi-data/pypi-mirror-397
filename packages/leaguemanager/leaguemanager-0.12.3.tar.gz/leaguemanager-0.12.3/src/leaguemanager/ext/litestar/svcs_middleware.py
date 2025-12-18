import attrs
import svcs
from advanced_alchemy._listeners import is_async_context
from sqlalchemy.orm import sessionmaker

from leaguemanager.lib.settings import get_settings
from litestar import Litestar
from litestar.datastructures import MutableScopeHeaders, State
from litestar.enums import ScopeType
from litestar.middleware import ASGIMiddleware
from litestar.types import ASGIApp, Message, Receive, Scope, Send

settings = get_settings()


class SVCSMiddleware(ASGIMiddleware):
    scopes = (ScopeType.HTTP, ScopeType.WEBSOCKET)

    async def handle(self, scope: Scope, receive: Receive, send: Send, next_app: ASGIApp) -> None:
        app_state = scope["app"].state
        print("In SVCS Middleware, adding container...")

        async with svcs.Container(app_state[settings.keys.svcs_registry]) as lm:
            scope["state"][settings.keys.svcs_container] = lm

            return await next_app(scope, receive, send)
