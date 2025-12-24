from cattle_grid.extensions.load import (
    load_extensions,
    set_globals,
    collect_method_information,
)
from cattle_grid.exchange.info import exchange_method_information
from cattle_grid.app import app_globals


def init_extensions(settings):
    extensions = load_extensions(settings)

    set_globals(extensions)

    app_globals.method_information = (
        collect_method_information(extensions) + exchange_method_information
    )

    return extensions
