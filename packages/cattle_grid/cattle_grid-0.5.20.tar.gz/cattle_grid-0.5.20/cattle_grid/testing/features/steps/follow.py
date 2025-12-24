import logging
from behave_auto_docstring import when, given
from uuid import uuid4

logger = logging.getLogger(__name__)


@when('"{alice}" sends "{bob}" a Follow Activity')  # type: ignore
async def send_follow(context, alice, bob):
    """Sends a follow Activity. Stores the follow activity in `context.follow_activity`"""
    alice_actor = context.actors[alice]
    bob_id = context.actors[bob].id

    context.follow_id = "follow:" + str(uuid4())

    context.follow_activity = alice_actor.activity_factory.follow(
        bob_id, id=context.follow_id
    ).build()

    await alice_actor.send_message(context.follow_activity)


@when('"{actor}" sends an Accept to this Follow Activity')  # type: ignore
async def accept_follow_request(context, actor):
    """Checks that Alice received a follow Activity and then
    accepts this follow activity"""
    result = await context.connections[actor].next_incoming()
    received_activity = result.get("data")
    if "raw" in received_activity:
        received_activity = received_activity["raw"]

    logger.debug("Got follow request:")
    logger.debug(received_activity)

    assert received_activity["type"] == "Follow"

    follow_id = received_activity["id"]
    to_follow = received_activity["actor"]

    alice = context.actors[actor]
    activity = alice.activity_factory.accept(follow_id, to={to_follow}).build()
    activity["id"] = "accept:" + str(uuid4())

    await alice.send_message(activity)


@given('"{bob}" follows "{alice}"')  # type: ignore
@when('"{bob}" follows "{alice}"')  # type: ignore
def actor_follows_other(context, bob, alice):
    """Combination of two steps,  this is the same as

    ```gherkin
    When "Alice" sends "Bob" a Follow Activity
    And "Bob" sends an Accept to this Follow Activity
    ```
    """
    context.execute_steps(
        f"""
        When "{bob}" sends "{alice}" a Follow Activity
        And "{alice}" sends an Accept to this Follow Activity
    """
    )


@given('"{bob}" follows auto-following "{alice}"')  # type: ignore
@when('"{bob}" follows auto-following "{alice}"')  # type: ignore
def actor_follows_auto_following_other(context, bob, alice):
    """Combination of two steps, this is the same as

    ```gherkin
    When "Alice" sends "Bob" a Follow Activity
    Then "Bob" receives an activity
    And the received activity is of type "Accept"
    ```
    """
    context.execute_steps(
        f"""
        When "{bob}" sends "{alice}" a Follow Activity
        Then "{bob}" receives an activity
        And the received activity is of type "Accept"
    """
    )


@when('"{bob}" sends "{alice}" an Undo Follow Activity')  # type: ignore
async def send_undo_follow(context, bob, alice):
    """Sends an Undo Follow activity for the follow activity
    with id stored in `context.follow_activity`."""
    actor = context.actors[bob]
    activity = actor.activity_factory.undo(context.follow_activity).build()
    if isinstance(activity["object"], dict):
        activity["object"] = activity["object"]["id"]

    activity["id"] = "undo:" + str(uuid4())
    await actor.send_message(activity)


@given('"{alice}" automatically accepts followers')  # type: ignore
async def automatically_accept_followers(context, alice):
    """FIXME: Should toggle"""

    actor = context.actors[alice]

    await actor.publish(
        "update_actor",
        {"actor": actor.id, "autoFollow": True},
    )


@when('"{alice}" sends "{bob}" a Reject Follow Activity')  # type: ignore
async def send_reject_follow(context, alice, bob):
    """Sends an Undo Follow activity for the follow activity
    with id stored in `context.follow_activity`."""
    actor = context.actors[alice]

    activity = actor.activity_factory.reject(context.follow_activity).build()
    if isinstance(activity["object"], dict):
        activity["object"] = activity["object"]["id"]

    activity["id"] = "reject:" + str(uuid4())

    await actor.send_message(activity)
