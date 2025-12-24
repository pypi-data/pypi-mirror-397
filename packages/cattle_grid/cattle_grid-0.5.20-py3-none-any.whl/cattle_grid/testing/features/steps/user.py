import logging
import random
from behave_auto_docstring import given, when, then
from bovine.clients import lookup_uri_with_webfinger

from cattle_grid.app import app_globals

from cattle_grid.config import load_settings
from cattle_grid.database import database_session
from cattle_grid.manage.actor import ActorManager
from cattle_grid.model.exchange import UpdateActorMessage

logger = logging.getLogger(__name__)


@given('A new user called "{username}" on "{hostname}"')
def new_user_on_server(context, username, hostname):
    context.execute_steps(
        f"""
        Given An account called "{username}"
        Given "{username}" created an actor on "{hostname}" called "{username}"
        """
    )


@given('A new user called "{username}"')
def new_user(context, username):
    """Creates a new user. The base_url to use is chosen randomly from
    the base_urls allowed in the frontend config.
    """

    base_urls = app_globals.application_config.frontend_config.base_urls

    hostname = random.choice(base_urls).removeprefix("http://")

    context.execute_steps(
        f"""
        Given A new user called "{username}" on "{hostname}"
        """
    )


@when('"{alice}" updates her profile')
async def update_profile(context, alice):
    for connection in context.connections.values():
        await connection.clear_incoming()

    alice_actor = context.actors[alice]
    msg = UpdateActorMessage(
        actor=alice_actor.id, profile={"summary": "I love cows"}
    ).model_dump()

    await alice_actor.publish("update_actor", msg)


@when('"{alice}" fetches her profile')
async def fetch_profile(context, alice):
    """
    The profile is stored in `context.profile`
    """

    alice_actor = context.actors[alice]
    context.profile = await alice_actor.fetch(alice_actor.id)

    assert isinstance(context.profile, dict)


@when('"{alice}" deletes herself')
@when('"{alice}" deletes himself')
async def actor_deletes_themselves(context, alice):
    alice_actor = context.actors[alice]

    await alice_actor.publish(
        "delete_actor",
        {
            "actor": alice_actor.id,
        },
    )


@given('"{alice}" is in the "{group_name}" group')
async def in_group(context, alice, group_name):
    alice_id = context.actors[alice].id
    config = load_settings()

    async with database_session(db_url=config.get("db_url")) as session:  # type: ignore
        manager = ActorManager(session=session, actor_id=alice_id)

        await manager.add_to_group(group_name)


@given('the actor "{boss_handle}" is called "{boss_name}"')
def register_boss_actor(context, boss_handle, boss_name):
    context.execute_steps(f'When One queries webfinger for "{boss_handle}"')

    actor_name = list(context.connections.keys())[0]

    context.execute_steps(
        f'When "{actor_name}" retrieves the object with id "{context.actor_uri}"'
    )

    context.actors[boss_name] = context.result


@when('One queries webfinger for "{resource}"')
async def query_webfinger(context, resource):
    context.actor_uri, _ = await lookup_uri_with_webfinger(
        context.session, resource, domain="http://abel"
    )


@then("An actor URI is returned")
def actor_uri_returned(context):
    assert context.actor_uri
