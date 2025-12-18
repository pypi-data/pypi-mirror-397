from typing import TYPE_CHECKING, Any, Callable, Coroutine, Optional, cast

import svcs
from attrs import define, field
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Session, sessionmaker

from leaguemanager import LeagueManager
from leaguemanager.lib.settings import get_settings
from litestar.constants import HTTP_DISCONNECT, HTTP_RESPONSE_START, WEBSOCKET_CLOSE, WEBSOCKET_DISCONNECT
from litestar.types import Message, Scope

if TYPE_CHECKING:
    from advanced_alchemy.config import SQLAlchemyAsyncConfig, SQLAlchemySyncConfig

    from litestar.datastructures import State


settings = get_settings()


@define
class LMConfig:
    """Configuration for the LeagueManager plugin."""

    league_manager: LeagueManager | None = None
    include_auth: bool = True

    league_manager_state_key: str = field(default=settings.keys.league_manager)
    sync_service_provider_key: str = field(default=settings.keys.db_sync_service)
    async_service_provider_key: str = field(default=settings.keys.db_async_service)
    svcs_registry_key: str = field(init=False, default=settings.keys.svcs_registry)
    svcs_container_key: str = field(init=False, default=settings.keys.svcs_container)
    alchemy_config_key: str = field(init=False, default="lm_alchemy_config")
    sessionmaker_key: str = field(init=False, default="lm_sessionmaker_class")
    session_dependency_key: str = field(init=False, default="db_session")

    _before_send_handler: Callable[[Message, Scope], None] | None = field(init=False, default=None)

    def __attrs_post_init__(self) -> None:
        if self.league_manager is None:
            try:
                from leaguemanager import LeagueManager

                self.league_manager = LeagueManager()
            except ImportError as e:
                raise ImportError("LeagueManager is not installed. Please install it to use the LM Dashboard.") from e

        if settings.db.commit_type is None:
            handler = self.make_default_sync_handler()
            self._before_send_handler = handler

        if not settings.db.commit_type:
            self._before_send_handler = self.make_default_sync_handler()
        if settings.db.async_url == "autocommit":
            self._before_send_handler = self.make_autocommit_sync_handler()
        if settings.db.commit_type == "autocommit_include_redirects":
            self._before_send_handler = self.make_autocommit_sync_handler(commit_on_redirect=True)

    @property
    def aa_sync_config(self) -> "SQLAlchemySyncConfig":
        """Get the SQLAlchemy sync configuration."""
        return cast(SQLAlchemySyncConfig, self.league_manager.container.get(SQLAlchemySyncConfig))

    @property
    def aa_async_config(self) -> "SQLAlchemyAsyncConfig":
        """Get the SQLAlchemy async configuration."""
        return cast(SQLAlchemyAsyncConfig, self.league_manager.container.get(SQLAlchemyAsyncConfig))

    def provide_sync_session(self, state: "State", scope: "Scope") -> Session:
        """Provide a synchronous SQLAlchemy session."""

        session = cast("Optional[Session]", scope.get(settings.keys.session_scope))
        print(scope)
        if not session:
            print("Creating new session")
            cont = cast(svcs.Container, state[settings.keys.svcs_container])
            session = cast(sessionmaker, cont.get(sessionmaker))
            scope[settings.keys.session_scope] = session

        return session

    async def provide_async_session(self, state: "State", scope: "Scope") -> AsyncSession:
        """Provide an asynchronous SQLAlchemy session."""

        session = cast("Optional[AsyncSession]", scope.get(settings.keys.session_scope))

        if not session:
            print("Creating new async session")
            cont = cast(svcs.Container, state[settings.keys.svcs_container])
            session = cast(async_sessionmaker, await cont.aget(async_sessionmaker))
            scope[settings.keys.session_scope] = session

        return session

    def make_default_sync_handler(
        self,
        session_scope_key: str = settings.keys.session_scope,
    ) -> Callable[[Message, Scope], None]:
        def handler(message: "Message", scope: "Scope") -> None:
            session = cast("Optional[Session]", scope["app"].state.get(session_scope_key, None))
            if session and message["type"] in (
                HTTP_RESPONSE_START,
                HTTP_DISCONNECT,
                WEBSOCKET_CLOSE,
                WEBSOCKET_DISCONNECT,
            ):
                session.close()
                scope["app"].state[session_scope_key] = None
            print("Before send handler (aka CLEANUP TIME)")

        return handler

    def make_autocommit_sync_handler(
        self,
        commit_on_redirect: bool = False,
        extra_commit_statuses: "Optional[set[int]]" = None,
        extra_rollback_statuses: "Optional[set[int]]" = None,
        session_scope_key: str = settings.keys.session_scope,
    ) -> "Callable[[Message, Scope], None]":
        """Set up the handler to issue a transaction commit or rollback based on specified status codes
        Args:
            commit_on_redirect: Issue a commit when the response status is a redirect (``3XX``)
            extra_commit_statuses: A set of additional status codes that trigger a commit
            extra_rollback_statuses: A set of additional status codes that trigger a rollback
            session_scope_key: The key to use within the application state

        Raises:
            ValueError: If extra rollback statuses and commit statuses share any status codes

        Returns:
            The handler callable
        """
        if extra_commit_statuses is None:
            extra_commit_statuses = set()

        if extra_rollback_statuses is None:
            extra_rollback_statuses = set()

        if len(extra_commit_statuses & extra_rollback_statuses) > 0:
            msg = "Extra rollback statuses and commit statuses must not share any status codes"
            raise ValueError(msg)

        commit_range = range(200, 400 if commit_on_redirect else 300)

        async def handler(message: "Message", scope: "Scope") -> None:
            """Handle commit/rollback, closing and cleaning up sessions before sending.

            Args:
                message: ASGI-``Message``
                scope: An ASGI-``Scope``

            """
            print("Im in the handler")
            session = cast("Optional[Session]", scope["app"].state.get(session_scope_key, None))
            try:
                if session is not None and message["type"] == HTTP_RESPONSE_START:
                    if (message["status"] in commit_range or message["status"] in extra_commit_statuses) and message[
                        "status"
                    ] not in extra_rollback_statuses:
                        await session.commit()
                    else:
                        await session.rollback()
            finally:
                if session and message["type"] in (WEBSOCKET_CLOSE, WEBSOCKET_DISCONNECT, HTTP_DISCONNECT):
                    await session.close()
                    scope["app"].state[session_scope_key] = None

        return handler


def make_default_async_handler(
    session_scope_key: str = settings.keys.session_scope,
) -> "Callable[[Message, Scope], Coroutine[Any, Any, None]]":
    """Set up the handler to issue a transaction commit or rollback based on specified status codes
    Args:
        session_scope_key: The key to use within the application state

    Returns:
        The handler callable
    """

    async def handler(message: "Message", scope: "Scope") -> None:
        """Handle commit/rollback, closing and cleaning up sessions before sending.

        Args:
            message: ASGI-``Message``
            scope: An ASGI-``Scope``
        """
        session = cast("Optional[AsyncSession]", scope["app"].state.get(session_scope_key, None))
        if session and message["type"] in (
            HTTP_RESPONSE_START,
            HTTP_DISCONNECT,
            WEBSOCKET_CLOSE,
            WEBSOCKET_DISCONNECT,
        ):
            await session.close()
            scope["app"].state[session_scope_key] = None

    return handler


def autocommit_handler_maker(
    commit_on_redirect: bool = False,
    extra_commit_statuses: Optional[set[int]] = None,
    extra_rollback_statuses: Optional[set[int]] = None,
    session_scope_key: str = settings.keys.session_scope,
) -> "Callable[[Message, Scope], Coroutine[Any, Any, None]]":
    """Set up the handler to issue a transaction commit or rollback based on specified status codes
    Args:
        commit_on_redirect: Issue a commit when the response status is a redirect (``3XX``)
        extra_commit_statuses: A set of additional status codes that trigger a commit
        extra_rollback_statuses: A set of additional status codes that trigger a rollback
        session_scope_key: The key to use within the application state

    Raises:
        ValueError: If the extra commit statuses and extra rollback statuses share any status codes

    Returns:
        The handler callable
    """
    if extra_commit_statuses is None:
        extra_commit_statuses = set()

    if extra_rollback_statuses is None:
        extra_rollback_statuses = set()

    if len(extra_commit_statuses & extra_rollback_statuses) > 0:
        msg = "Extra rollback statuses and commit statuses must not share any status codes"
        raise ValueError(msg)

    commit_range = range(200, 400 if commit_on_redirect else 300)

    async def handler(message: "Message", scope: "Scope") -> None:
        """Handle commit/rollback, closing and cleaning up sessions before sending.

        Args:
            message: ASGI-``litestar.types.Message``
            scope: An ASGI-``litestar.types.Scope``
        """
        session = cast("Optional[AsyncSession]", scope["app"].state.get(session_scope_key, None))
        try:
            if session is not None and message["type"] == HTTP_RESPONSE_START:
                if (message["status"] in commit_range or message["status"] in extra_commit_statuses) and message[
                    "status"
                ] not in extra_rollback_statuses:
                    await session.commit()
                else:
                    await session.rollback()
        finally:
            if session and message["type"] in (
                HTTP_RESPONSE_START,
                HTTP_DISCONNECT,
                WEBSOCKET_CLOSE,
                WEBSOCKET_DISCONNECT,
            ):
                await session.close()
                scope["app"].state[session_scope_key] = None

    return handler
