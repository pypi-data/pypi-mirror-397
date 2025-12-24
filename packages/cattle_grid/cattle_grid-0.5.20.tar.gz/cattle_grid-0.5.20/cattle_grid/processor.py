import logging
from faststream import FastStream

from contextlib import asynccontextmanager

from cattle_grid.app import app_globals
from cattle_grid.app.lifespan import common_lifespan

from .app.extensions import init_extensions
from .app.router import add_routers_to_broker, create_broker

from .extensions.load import (
    lifespan_from_extensions,
)

logging.basicConfig(level=logging.INFO)

extensions = init_extensions(app_globals.config)

broker = create_broker()
add_routers_to_broker(broker, extensions, app_globals.config)


@asynccontextmanager
async def lifespan():
    async with common_lifespan():
        async with lifespan_from_extensions(extensions):
            yield


app = FastStream(broker, lifespan=lifespan)


@app.after_startup
async def declare_exchanges() -> None:
    if app_globals.internal_exchange:
        await broker.declare_exchange(app_globals.internal_exchange)
    if app_globals.activity_exchange:
        await broker.declare_exchange(app_globals.activity_exchange)
