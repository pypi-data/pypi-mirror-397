from collections.abc import Awaitable
from typing import Callable
import aiohttp
from faststream.rabbit import RabbitBroker, RabbitExchange
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine

from cattle_grid.app.load_globals import (
    construct_account_exchange,
    construct_activity_exchange,
    construct_internal_exchange,
    load_rewrite_rules,
)
from cattle_grid.config import load_settings
from cattle_grid.config.application import ApplicationConfig
from cattle_grid.config.rewrite import RewriteConfiguration

from cattle_grid.model.extension import MethodInformationModel
from cattle_grid.model.lookup import LookupMethod

config = load_settings()

application_config: ApplicationConfig = ApplicationConfig.from_settings(config)
rewrite_rules: RewriteConfiguration = load_rewrite_rules(config)

internal_exchange: RabbitExchange = construct_internal_exchange(config)
activity_exchange: RabbitExchange = construct_activity_exchange(config)
account_exchange: RabbitExchange = construct_account_exchange(config)

broker: RabbitBroker | None = None

engine: AsyncEngine | None = None
async_session_maker: Callable[[], AsyncSession] | None = None
session: aiohttp.ClientSession | None = None

method_information: list[MethodInformationModel]
transformer: Callable[[dict], Awaitable[dict]] | None = None
lookup: LookupMethod | None = None
