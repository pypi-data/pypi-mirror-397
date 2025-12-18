from __future__ import annotations

from contextlib import asynccontextmanager, contextmanager
from inspect import isclass
from logging import config
from pathlib import Path
from typing import TYPE_CHECKING, Any, AsyncGenerator, Generator, overload

from advanced_alchemy.config import SQLAlchemyAsyncConfig, SQLAlchemySyncConfig
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService
from attrs import define, field
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import Session, sessionmaker
from svcs import Container, Registry

from leaguemanager._types import (
    T1,
    T2,
    T3,
    T4,
    T5,
    AsyncServiceT,
    AsyncSessionT,
    ImporterT,
    ScheduleServiceT,
    SQLAlchemyAsyncConfigT,
    SQLAlchemySyncConfigT,
    SyncServiceT,
)
from leaguemanager.db import async_config, sync_config
from leaguemanager.db.engine_factory import create_async_db_engine, create_sync_db_engine
from leaguemanager.dependency.loader import DynamicObjectLoader
from leaguemanager.dependency.managers import (
    ImporterManagement,
    SchedulerManagement,
    ServiceManagement,
    service_provider,
)
from leaguemanager.lib.settings import get_settings
from leaguemanager.lib.toolbox import module_to_os_path

__all__ = ["LeagueManager"]

get_settings.cache_clear()
settings = get_settings()


@define
class LeagueManager:
    """Registry for managing services.

    TODO: Serve up async repos/services

    If no `Registry` is provided, one will be created. Keep in mind that there should only
    be one registry per application.

    Services are kept in an svcs `Container` and are provided as needed. This includes a
    database session, League Manager "repositories" and "services" (which themselves provide
    common database operations), Advanced Alchemy database configuration objects, and other
    league related services (such as importers and schedulers).

    Attributes:
        service_registry (Registry | None): An `svcs` Registry for managing services.
        loader (DynamicObjectLoader): A DynamicObjectLoader for loading specific objects.
        local_base_dir (Path): The local base directory. Uses `settings.APP_DIR` by default.
        local_root_dir (Path): The local root directory. Uses `settings.APP_ROOT` by default.
        aa_config_dir (Path): The Advanced Alchemy configuration directory.
        get_session (Generator[Session, Any, None]): A generator for a database session.
        get_async_session (AsyncGenerator[AsyncSession, Any]): A generator for an async database session.
        sync_services (list[type[SyncServiceT]]): List of services for sync database operations.
        async_services (list[type[AsyncServiceT]]): List of services for async database operations.

    Example:
        >>> registry = LeagueManager()
        >>> season_service = registry.provide_db_service(SeasonSyncService)
        >>> team_service = registry.provide_db_service(TeamSyncService)
        >>>
        >>> season_service.list()  #  List all seasons
        >>> team_service.count()  #  Count number of teams

    """

    registry: Registry | None = field(default=None)
    loader: DynamicObjectLoader = field(default=DynamicObjectLoader())

    local_services_dir: Path | None = None

    sync_services: list[type[SyncServiceT]] = field(init=False)
    async_services: list[type[AsyncServiceT]] = field(init=False)
    async_config: SQLAlchemySyncConfigT | SQLAlchemyAsyncConfigT = field(default=async_config)
    sync_config: SQLAlchemySyncConfigT | SQLAlchemyAsyncConfigT = field(default=sync_config)

    def __attrs_post_init__(self):
        if not self.registry:
            self.registry = Registry()

        # Get all services
        _importers = self.loader.get_importer_services(settings.template_loader_dir)
        _schedulers = self.loader.get_schedule_services(settings.schedule_loader_dir)
        self.sync_services = self.loader.get_aa_services()
        self.async_services = self.loader.get_aa_services(is_async=True)

        # Include additional AA services from the local services directory
        if self.local_services_dir and self.local_services_dir is not settings.db_services_dir:
            svc_loader = self.loader.local_app(service_dir=self.local_services_dir)
            self.sync_services += svc_loader.get_aa_services()
            self.async_services += svc_loader.get_aa_services(is_async=True)

        # If running from within host application, migration path is set within project
        # otherwise, it sets the migration environment relative to the user's app.

        # if settings.app_name not in str(settings.user_app.app_dir):
        #     print("Setting migration path to local...")
        #     self.async_config.alembic_config.script_location = str(settings.user_app.app_dir / "migrations")
        #     self.async_config.alembic_config.script_config = str(settings.user_app.app_dir / "alembic.ini")
        # self.async_config.alembic_config.template_path = str(settings.alembic.template_path)
        # self.sync_config.alembic_config.script_location = str(settings.user_app.app_dir / "migrations")
        # self.sync_config.alembic_config.script_config = str(settings.user_app.app_dir / "alembic.ini")
        # self.async_config.alembic_config.template_path = str(settings.alembic.template_path)

        # Register objects
        self.registry.register_factory(Engine, create_sync_db_engine)
        self.registry.register_factory(AsyncEngine, create_async_db_engine)

        self.registry.register_value(SQLAlchemySyncConfig, self.sync_config)
        self.registry.register_value(SQLAlchemyAsyncConfig, self.async_config)

        self.register_session_maker()
        self.register_async_session_maker()

        for _importer in _importers:
            # self.register_importer_service(importer_type=_importer)
            importer_type: type[ImporterT] = _importer
            self.registry.register_value(importer_type, _importer())

        for _scheduler in _schedulers:
            # self.register_scheduler_service(scheduler_type=_scheduler)
            scheduler_type: type[ScheduleServiceT] = _scheduler
            self.registry.register_value(scheduler_type, _scheduler())

        for service_type in self.sync_services:
            self.register_db_service(service_type=service_type)

        for service_type in self.async_services:
            self.test_register_async(service_type=service_type)

    @property
    def container(self):
        return Container(self.registry)

    @overload
    async def get(self, type_1: type[T1]) -> T1: ...

    @overload
    async def get(
        self,
        type_1: type[T1],
        type_2: type[T2],
    ) -> tuple[T1, T2]: ...

    @overload
    async def get(
        self,
        type_1: type[T1],
        type_2: type[T2],
        type_3: type[T3],
    ) -> tuple[T1, T2, T3]: ...

    @overload
    async def get(
        self,
        type_1: type[T1],
        type_2: type[T2],
        type_3: type[T3],
        type_4: type[T4],
    ) -> tuple[T1, T2, T3, T4]: ...

    @overload
    async def get(
        self,
        type_1: type[T1],
        type_2: type[T2],
        type_3: type[T3],
        type_4: type[T4],
        type_5: type[T5],
    ) -> tuple[T1, T2, T3, T4, T5]: ...

    async def get(self, *types: type[Any]) -> Any:
        return await self.container.aget(*types)

    def register_db_service(self, service_type: type[SyncServiceT]) -> None:
        """Register a League Manager service based on its type."""
        session = self.container.get(sessionmaker)
        self.registry.register_value(service_type, service_type(session=session))

    def test_register_async(self, service_type: type[AsyncServiceT]) -> None:
        """Test method to register an async League Manager service based on its type."""

        async def _async_service_factory():
            session = self.container.aget(async_sessionmaker)
            return service_type(session=await session)

        self.registry.register_factory(service_type, _async_service_factory)

    def register_async_db_service(self, service_type: type[AsyncServiceT]) -> None:
        """Register an async League Manager service based on its type."""
        _service = ServiceManagement(service_type=service_type)
        self.registry.register_value(service_type, next(_service.get_service))

    def register_session_maker(self) -> None:
        """Register a sync session."""
        self.registry.register_factory(sessionmaker, self.sync_config.create_session_maker())

    def register_async_session_maker(self) -> None:
        """Register an async session."""
        self.registry.register_factory(async_sessionmaker, self.async_config.create_session_maker())

    @property
    def provide_sync_session(self) -> Session:
        sync_config = self.container.get(SQLAlchemySyncConfig)
        with sync_config.get_session() as session:
            return session

    @overload
    def _provide_db_service(self, service_type: type[SyncServiceT]) -> SyncServiceT: ...

    @overload
    def _provide_db_service(self, service_type: type[AsyncServiceT]) -> AsyncServiceT: ...

    def _provide_db_service(
        self, service_type: type[SyncServiceT] | type[AsyncServiceT]
    ) -> SyncServiceT | AsyncServiceT:
        print(f"Providing service for type: {service_type}")
        print(f"is subclass of async?: {issubclass(service_type, SQLAlchemyAsyncRepositoryService)}")
        if isclass(service_type) and issubclass(service_type, SQLAlchemyAsyncRepositoryService):
            print(f"Got async service {service_type}: {isclass(service_type)}")
            return Container(self.registry).aget(service_type)

        print(f"Got sync service {service_type}: {isclass(service_type)}")
        session = self.container.get(sessionmaker)
        return service_provider(service_type, session=session)

    def provide_db_service(self, service_type: type[SyncServiceT]) -> type[SyncServiceT]:
        """Provide a League Manager service based on its type."""
        return Container(self.registry).get(service_type)

    def provide_async_db_service(self, service_type: type[AsyncServiceT]) -> type[AsyncServiceT]:
        """Provide an async League Manager service based on its type."""
        return Container(self.registry).aget(service_type)

    def provide_importer_service(self, importer_type: type[ImporterT]) -> ImporterT:
        """Provide an importer service based on the type specified."""
        return Container(self.registry).get(importer_type)

    def provide_scheduler_service(self, scheduler_type: type[ScheduleServiceT]) -> ScheduleServiceT:
        """Provide a scheduling service based on the type specified."""
        return Container(self.registry).get(scheduler_type)
