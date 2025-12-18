import os
from contextlib import asynccontextmanager, contextmanager
from typing import Any, AsyncGenerator, Generator

from advanced_alchemy.config import (
    AlembicAsyncConfig,
    AlembicSyncConfig,
    AsyncSessionConfig,
    SQLAlchemyAsyncConfig,
    SQLAlchemySyncConfig,
    SyncSessionConfig,
)

# from litestar.plugins.sqlalchemy import AsyncSessionConfig, SQLAlchemyAsyncConfig
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from leaguemanager.db.engine_factory import create_async_db_engine, create_sync_db_engine
from leaguemanager.lib.settings import get_settings
from leaguemanager.models.base import metadata

__all__ = [
    "sync_alembic_config",
    "sync_config",
    "async_alembic_config",
    "async_config",
]


settings = get_settings()


def _is_lm_app() -> bool:
    """Checks if current application is the League Manager app."""
    if settings.root_dir == settings.user_app.root_dir:
        return True
    return False


root_dir = settings.root_dir if _is_lm_app() else settings.user_app.root_dir
app_dir = settings.app_dir if _is_lm_app() else settings.user_app.app_dir

if not settings.alembic.config_file_path:
    script_config = root_dir / "alembic.ini"
else:
    script_config = settings.alembic.config_file_path


if not settings.alembic.migration_path:
    script_location = (app_dir / "db/migrations") if _is_lm_app() else (app_dir / "migrations")
else:
    script_location = settings.alembic.migration_path


# Sync DB Setup
# Note: Alembic currently only accepts path strings for settings

sync_alembic_config = AlembicSyncConfig(
    version_table_name="alembic_version",
    script_config=str(script_config),
    script_location=str(script_location),
    template_path=str(settings.alembic.template_path),
)


sync_config = SQLAlchemySyncConfig(
    engine_instance=create_sync_db_engine(),
    alembic_config=sync_alembic_config,
    metadata=metadata,
    session_config=SyncSessionConfig(expire_on_commit=False),
    bind_key="lm_sync",
    # session_scope_key="lm_sync_session",
    # engine_dependency_key="lm_sync_engine",
)


# Async DB Setup
# Note: Alembic currently only accepts path strings for settings

async_alembic_config = AlembicAsyncConfig(
    version_table_name="alembic_version",
    script_config=str(script_config),
    script_location=str(script_location),
    template_path=str(settings.alembic.template_path),
)


async_config = SQLAlchemyAsyncConfig(
    engine_instance=create_async_db_engine(),
    # before_send_handler=settings.db.commit_type or None,
    alembic_config=async_alembic_config,
    metadata=metadata,
    session_config=AsyncSessionConfig(expire_on_commit=False),
    bind_key="lm_async",
    # session_scope_key="lm_async_session",
    # engine_dependency_key="lm_async_engine",
)
