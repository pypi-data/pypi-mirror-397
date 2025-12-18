from __future__ import annotations

import typer
from advanced_alchemy.config import SQLAlchemyAsyncConfig, SQLAlchemySyncConfig
from sqlalchemy.orm import Session

from leaguemanager._types import (
    ImporterT,
    SQLAlchemyAsyncConfigT,
    SQLAlchemySyncConfigT,
    SyncRepositoryT,
    SyncServiceT,
)
from leaguemanager.dependency import LeagueManager

lm = LeagueManager()


def provide_manager_service(param: typer.CallbackParam) -> SyncServiceT | SyncRepositoryT:
    # return registry.provide_db_service(service_type=param.type.func)

    return lm.container.get(param.type.func)


def provide_sync_db_session() -> Session:
    return lm.provide_sync_session


def provide_sync_db_config() -> SQLAlchemySyncConfig:
    """Provide the synchronous SQLAlchemy configuration."""
    return lm.provide_sync_config


def provide_async_db_config() -> SQLAlchemyAsyncConfig:
    """Provide the asynchronous SQLAlchemy configuration."""
    return lm.container.get(SQLAlchemyAsyncConfig)


def provide_importer_service(param: typer.CallbackParam) -> ImporterT:
    """Provide an importer service based on the type specified in the callback parameter."""
    importer_type = param.type.func
    return lm.provide_importer_service(importer_type=importer_type)


def provide_scheduler_service(param: typer.CallbackParam) -> SyncServiceT:
    """Provide a scheduling service based on the type specified in the callback parameter."""
    scheduler_type = param.type.func
    return lm.provide_scheduler_service(scheduler_type=scheduler_type)
