from cattle_grid.app import app_globals
from faststream.rabbit import RabbitBroker

from typing import List

from cattle_grid.extensions import Extension

from cattle_grid.account.processing import create_account_router
from cattle_grid.activity_pub.processing import create_processing_router
from cattle_grid.exchange import create_router
from cattle_grid.testing.reporter import create_reporting_router

from cattle_grid.extensions.load import (
    add_routers_to_broker as extensions_add_routers_to_broker,
)
from cattle_grid.exchange.exception import exception_middleware


def create_broker():
    app_globals.broker = RabbitBroker(
        app_globals.application_config.amqp_url,  # type:ignore
        middlewares=[exception_middleware],
        **app_globals.application_config.faststream_options,
    )

    return app_globals.broker


def add_routers_to_broker(broker: RabbitBroker, extensions: List[Extension], settings):
    broker.include_router(create_account_router())
    broker.include_router(create_processing_router(app_globals.internal_exchange))

    if settings.enable_reporting:
        broker.include_router(create_reporting_router())

    broker.include_router(create_router())

    extensions_add_routers_to_broker(broker, extensions)
