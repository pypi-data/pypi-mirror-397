from __future__ import annotations

import contextlib
from logging import Logger
from typing import TYPE_CHECKING, AsyncGenerator, cast

import svcs
from advanced_alchemy.config import SQLAlchemyAsyncConfig
from sqlalchemy.orm import Session
from typing_extensions import override

from leaguemanager._types import (
    AsyncServiceT,
    SyncServiceT,
)
from leaguemanager.dependency.dependency_registry import LeagueManager
from leaguemanager.ext.litestar.config import LMConfig
from leaguemanager.ext.litestar.svcs_middleware import SVCSMiddleware
from leaguemanager.lib.settings import get_settings
from leaguemanager.services.competition.season import SeasonAsyncService, SeasonService
from litestar.di import Provide
from litestar.exceptions import ImproperlyConfiguredException
from litestar.plugins import InitPlugin

from .oauth import AccessTokenState, OAuth2AuthorizeCallback, OAuth2Token

if TYPE_CHECKING:
    from litestar.app import Litestar
    from litestar.config.app import AppConfig
    from litestar.datastructures.state import State
    from litestar.types import BeforeMessageSendHookHandler, Message, Scope

settings = get_settings()

logger = Logger(__name__)


class LMPlugin(InitPlugin):
    """Plugin to integrate LeagueManager into Litestar applications."""

    def __init__(self, config: LMConfig) -> None:
        """Initialize the plugin with the provided configuration."""
        self._config = config

    @property
    def config(self) -> LMConfig:
        return self._config

    def _get_lm_from_state(self, state: State) -> LeagueManager:
        try:
            return cast(LeagueManager, state.get(self.config.league_manager_state_key))
        except Exception as e:
            logger.error(f"Error retrieving LeagueManager from state: {e}")
            raise ImproperlyConfiguredException("LeagueManager is not available in the app state.") from e

    def provide_svcs_container(self, state: State) -> svcs.Container:
        """Provide the svcs Container from the app state."""
        lm = self._get_lm_from_state(state)
        return lm.container

    def sync_db_service(self, state: State, scope: Scope) -> type[SyncServiceT]:
        """Provide the LeagueManager instance from the app state."""
        lm = self._get_lm_from_state(state)

        return lm.provide_db_service

    def async_db_service(self, state: State) -> type[AsyncServiceT]:
        """Provide the LeagueManager instance from the app state."""
        lm = self._get_lm_from_state(state)
        return lm.provide_async_db_service

    def _db_service(self, state: State, scope: Scope) -> type[SyncServiceT] | type[AsyncServiceT]:
        lm = self._get_lm_from_state(state)
        print(f"plugin provider: {state=} and {scope=}")
        return lm._provide_db_service

    @contextlib.asynccontextmanager
    async def _lifespan(
        self,
        app: "Litestar",
    ) -> "AsyncGenerator[None, None]":
        deps = {
            self.config.league_manager_state_key: self.config.league_manager,
            self.config.svcs_registry_key: self.config.league_manager.registry,
            self.config.svcs_container_key: self.config.league_manager.container,
        }
        app.state.update(deps)
        try:
            yield
        finally:
            self.config.league_manager.registry.aclose()

    @override
    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        app_config.lifespan.append(self._lifespan)
        app_config.dependencies.update(
            {
                # self.config.session_dependency_key: Provide(self.config.provide_async_session),
                self.config.session_dependency_key: Provide(self.config.provide_sync_session, sync_to_thread=False),
                self.config.svcs_container_key: Provide(self.provide_svcs_container, sync_to_thread=False),
                "db_service": Provide(self._db_service, sync_to_thread=False),
            }
        )
        app_config.signature_namespace.update(
            {
                "LeagueManager": LeagueManager,
            }
        )
        if self.config.include_auth:
            app_config.signature_namespace.update(
                {
                    "OAuth2AuthorizeCallback": OAuth2AuthorizeCallback,
                    "AccessTokenState": AccessTokenState,
                    "OAuth2Token": OAuth2Token,
                    "SeasonService": SeasonService,
                    "SeasonAsyncService": SeasonAsyncService,
                },
            )
        app_config.middleware.append(SVCSMiddleware())
        # app_config.before_send.append(cast("BeforeMessageSendHookHandler", self.config._before_send_handler))

        return app_config
