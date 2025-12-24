import asyncio
from behave import when, then


@when('"{alice}" publishes a "{moo}" animal sound to her followers')  # pyright: ignore[reportCallIssue]
async def send_sound(context, alice, moo):
    await asyncio.sleep(0.2)
    for connection in context.connections.values():
        await connection.clear_incoming()

    alice_actor = context.actors[alice]

    activity = (
        alice_actor.activity_factory.custom(type="AnimalSound", content="moo")
        .as_public()
        .build()
    )

    await alice_actor.publish_activity(activity)


@when('"{alice}" publishes a message "{text}" to her followers')  # pyright: ignore[reportCallIssue]
async def send_message(context, alice, text):
    await asyncio.sleep(0.3)
    for connection in context.connections.values():
        await connection.clear_incoming()

    alice_actor = context.actors[alice]

    note = alice_actor.object_factory.note(content=text).as_public().build()

    await alice_actor.publish_object(note)


@then('"{bob}" can retrieve the activity')  # pyright: ignore[reportCallIssue]
async def can_retrieve_activity(context, bob):
    result = await context.actors[bob].fetch(context.activity.get("id"))
    assert result
