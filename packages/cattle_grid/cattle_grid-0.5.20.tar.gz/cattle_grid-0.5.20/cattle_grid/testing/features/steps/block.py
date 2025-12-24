from uuid import uuid4
from behave import when, given


@given('"{alice}" blocks "{bob}"')  # type: ignore
@when('"{alice}" blocks "{bob}"')  # type: ignore
async def send_block(context, alice, bob):
    """
    ```gherkin
    When "Alice" blocks "Bob"
    ```

    The id of the block is stored in `context.block_id`
    """

    actor = context.actors[alice]
    bob_id = context.actors[bob].id

    activity = actor.activity_factory_with_id.custom(
        type="Block", object=bob_id, to={bob_id}
    ).build()

    context.block_id = activity.get("id")

    await actor.send_message(activity)


@when('"{bob}" unblocks "{alice}"')  # type: ignore
async def unblock(context, bob, alice):
    """Sends an Undo Block activity for
    the id stored in `context.block_id`.

    Usage:

    ```gherkin
    When "Bob" unblocks "Alice"
    ```
    """
    actor = context.actors[bob]
    alice_id = context.actors[alice].id

    activity = actor.activity_factory.custom(
        object=context.block_id, to={alice_id}, type="Undo"
    ).build()
    activity["id"] = "undo:" + str(uuid4())

    await actor.send_message(activity)
