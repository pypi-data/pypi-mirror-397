from collections.abc import Awaitable, Callable
from dynaconf import Dynaconf
from faststream.rabbit import RabbitExchange
from sqlalchemy.ext.asyncio import AsyncEngine
from cattle_grid.model.extension import MethodInformationModel
from cattle_grid.model.lookup import LookupMethod

from . import app_globals


def raise_if_none(exchange: RabbitExchange | None) -> RabbitExchange:
    if exchange is None:
        raise Exception("Exchange is not configured")
    return exchange


def get_internal_exchange() -> RabbitExchange:
    return raise_if_none(app_globals.internal_exchange)


def get_activity_exchange() -> RabbitExchange:
    return raise_if_none(app_globals.activity_exchange)


def get_account_exchange() -> RabbitExchange:
    return raise_if_none(app_globals.account_exchange)


def get_method_information() -> list[MethodInformationModel]:
    return app_globals.method_information


def get_transformer() -> Callable[[dict], Awaitable[dict]]:
    if app_globals.transformer is None:
        raise Exception("Transformer not initialized")
    return app_globals.transformer


def get_engine() -> AsyncEngine:
    if not app_globals.engine:
        raise ValueError("Engine not initialized")

    return app_globals.engine


def get_lookup() -> LookupMethod:
    if not app_globals.lookup:
        raise ValueError("Lookup not initialized")

    return app_globals.lookup


def get_config() -> Dynaconf:
    return app_globals.config


def get_broker():
    if not app_globals.broker:
        raise Exception("Broker not initialized")
    return app_globals.broker


def get_client_session():
    if not app_globals.session:
        raise Exception("Aiohttp ClientSession not initialized")
    return app_globals.session
