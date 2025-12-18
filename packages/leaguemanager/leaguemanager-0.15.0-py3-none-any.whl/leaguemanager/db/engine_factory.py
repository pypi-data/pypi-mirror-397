import os
from typing import TYPE_CHECKING

from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from leaguemanager.lib.settings import get_settings

settings = get_settings()


def create_sync_db_engine() -> "Engine":
    if _url := settings.db.sync_url:
        url = _url
    else:
        # If no URL is provided, default to a local SQLite database
        db_name = settings.db.sqlite_db_name
        data_dir = settings.db.sqlite_data_directory
        data_dir.mkdir(parents=True, exist_ok=True)

        url = f"sqlite:///{data_dir.stem}/{db_name}"
    if url.startswith("postgresql+pyscopg://"):
        engine = create_engine(
            url=url,
            future=True,
            echo=settings.db.echo,
            echo_pool=settings.db.echo_pool,
            pool_size=settings.db.pool_size,
            max_overflow=settings.db.pool_max_overflow,
            pool_timeout=settings.db.pool_timeout,
            pool_recycle=settings.db.pool_recycle,
            pool_pre_ping=settings.db.pool_pre_ping,
            pool_use_lifo=True,
        )
        return engine
    elif url.startswith("sqlite"):
        engine = create_engine(
            url=url,
            future=True,
            echo=settings.db.echo,
            echo_pool=settings.db.echo_pool,
            pool_size=settings.db.pool_size,
            max_overflow=settings.db.pool_max_overflow,
            pool_timeout=settings.db.pool_timeout,
            pool_recycle=settings.db.pool_recycle,
            pool_pre_ping=settings.db.pool_pre_ping,
            pool_use_lifo=True,
        )
        return engine


def create_async_db_engine() -> "AsyncEngine":
    if _url := settings.db.async_url:
        url = _url
    else:
        # If no URL is provided, default to a local SQLite database
        db_name = settings.db.sqlite_db_name
        data_dir = settings.db.sqlite_data_directory
        data_dir.mkdir(parents=True, exist_ok=True)

        url = f"sqlite+aiosqlite:///{data_dir.stem}/{db_name}"
    if url.startswith("postgresql+asyncpg://"):
        try:
            engine = create_async_engine(
                url=url,
                future=True,
                echo=settings.db.echo,
                echo_pool=settings.db.echo_pool,
                pool_size=settings.db.pool_size,
                max_overflow=settings.db.pool_max_overflow,
                pool_timeout=settings.db.pool_timeout,
                pool_recycle=settings.db.pool_recycle,
                pool_pre_ping=settings.db.pool_pre_ping,
                pool_use_lifo=True,
            )
        except Exception as e:
            print(f"Error creating async engine: {e}")
            raise
        return engine
    elif url.startswith("sqlite"):
        engine = create_async_engine(
            url=url,
            future=True,
            echo=settings.db.echo,
            echo_pool=settings.db.echo_pool,
            pool_size=settings.db.pool_size,
            max_overflow=settings.db.pool_max_overflow,
            pool_timeout=settings.db.pool_timeout,
            pool_recycle=settings.db.pool_recycle,
            pool_pre_ping=settings.db.pool_pre_ping,
            pool_use_lifo=True,
        )
        return engine
