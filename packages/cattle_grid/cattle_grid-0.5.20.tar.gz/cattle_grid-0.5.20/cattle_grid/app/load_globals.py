import logging

from dynaconf import Dynaconf
from faststream.rabbit import RabbitExchange, ExchangeType

from ..config.rewrite import RewriteConfiguration


logger = logging.getLogger(__name__)


def construct_account_exchange(config: Dynaconf) -> RabbitExchange:
    account_exchange_name = config.activity_pub.account_exchange  # type: ignore

    durable = True if account_exchange_name == "amq.topic" else False

    return RabbitExchange(
        account_exchange_name, type=ExchangeType.TOPIC, durable=durable
    )  # type: ignore


def construct_activity_exchange(config: Dynaconf) -> RabbitExchange:
    return RabbitExchange(
        config.activity_pub.exchange,  # type: ignore
        type=ExchangeType.TOPIC,
    )


def construct_internal_exchange(config: Dynaconf) -> RabbitExchange:
    return RabbitExchange(
        config.activity_pub.internal_exchange,  # type: ignore
        type=ExchangeType.TOPIC,
    )


def load_rewrite_rules(config: Dynaconf) -> RewriteConfiguration:
    return RewriteConfiguration.from_rules(config.get("rewrite"))
