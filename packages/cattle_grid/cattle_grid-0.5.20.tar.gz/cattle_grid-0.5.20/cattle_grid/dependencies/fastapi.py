"""
FastAPI uses [fastapi.Depends][] instead of [fast_depends.Depends][],
so when building a [fastapi.APIRouter][], one needs to use dependencies
using the former. These are provided in this package.
"""

import logging
import aiohttp

from typing import Annotated
from collections.abc import Callable, Awaitable
from dynaconf import Dynaconf

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, AsyncSession

from fastapi import Depends

from cattle_grid.app import access_methods
from cattle_grid.model.extension import MethodInformationModel

from .fastapi_internals import (
    ActivityExchangePublisherClass,
    ActivityExchangeRequesterClass,
)

logger = logging.getLogger(__name__)

SqlAsyncEngine = Annotated[AsyncEngine, Depends(access_methods.get_engine)]
"""Returns the SqlAlchemy AsyncEngine"""

Transformer = Annotated[
    Callable[[dict], Awaitable[dict]], Depends(access_methods.get_transformer)
]
"""The transformer loaded from extensions"""


MethodInformation = Annotated[
    list[MethodInformationModel], Depends(access_methods.get_method_information)
]
"""Returns the information about the methods that are a part of the exchange"""


async def with_fast_api_session(sql_engine: SqlAsyncEngine):
    async with async_sessionmaker(sql_engine)() as session:
        yield session


SqlSession = Annotated[AsyncSession, Depends(with_fast_api_session)]
"""Session annotation to be used with FastAPI"""


async def with_committing_sql_session(session: SqlSession):
    yield session
    await session.commit()


CommittingSession = Annotated[AsyncSession, Depends(with_committing_sql_session)]
"""Session annotation to be used with FastAPI. A commit is performed, after processing the request"""


Config = Annotated[Dynaconf, Depends(access_methods.get_config)]
"""Returns the configuration"""


ClientSession = Annotated[
    aiohttp.ClientSession, Depends(access_methods.get_client_session)
]
"""The [aiohttp.ClientSession][] used by the application"""


ActivityExchangePublisher = Annotated[Callable, Depends(ActivityExchangePublisherClass)]
"""Publisher to the activity exchange"""

ActivityExchangeRequester = Annotated[Callable, Depends(ActivityExchangeRequesterClass)]
"""Requester to the activity exchange"""
