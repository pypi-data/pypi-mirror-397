from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from advanced_alchemy.config import SQLAlchemyAsyncConfig, SQLAlchemySyncConfig
from advanced_alchemy.repository import SQLAlchemyAsyncRepository, SQLAlchemySyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService
from sqlalchemy.ext.asyncio import AsyncSession

from leaguemanager.models._types import ModelT
from leaguemanager.services.scheduling import (
    BracketSchedule,
    RoundRobinPlayoffSchedule,
    RoundRobinSchedule,
    TournamentSchedule,
)
from leaguemanager.services.template_loader.league_importer import Importer

# ModelT = TypeVar("ModelT")
SyncRepositoryT = TypeVar("RepositoryT", bound=SQLAlchemySyncRepository)
AsyncRepositoryT = TypeVar("RepositoryT", bound=SQLAlchemyAsyncRepository)
SyncServiceT = TypeVar("ServiceT", bound=SQLAlchemySyncRepositoryService[ModelT])
AsyncServiceT = TypeVar("ServiceT", bound=SQLAlchemyAsyncRepositoryService[ModelT])
AsyncSessionT = TypeVar("AsyncSessionT", bound=AsyncSession)
SQLAlchemySyncConfigT = TypeVar("SQLAlchemySyncConfigT", bound=SQLAlchemySyncConfig)
SQLAlchemyAsyncConfigT = TypeVar("SQLAlchemyAsyncConfigT", bound=SQLAlchemyAsyncConfig)
ImporterT = TypeVar("ImporterT", bound=Importer)
ScheduleServiceT = TypeVar(
    "ScheduleServiceT", bound=BracketSchedule | RoundRobinSchedule | RoundRobinPlayoffSchedule | TournamentSchedule
)
T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")
T5 = TypeVar("T5")
