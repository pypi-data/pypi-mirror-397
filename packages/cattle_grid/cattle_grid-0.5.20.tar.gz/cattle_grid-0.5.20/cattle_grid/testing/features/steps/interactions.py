from behave_auto_docstring import given, when


@when('"{alice}" likes the ActivityPub object')
async def alice_likes(context, alice):
    """Alice likes the object given by [alice_fetches_the_activity_pub_object][cattle_grid.testing.features.steps.fetch.alice_fetches_the_activity_pub_object]"""
    alice_actor = context.actors[alice]

    activity = (
        alice_actor.activity_factory.like(
            context.fetch_response.get("id"),
            to={context.fetch_response.get("attributedTo")},
        )
        .as_public()
        .build()
    )

    await alice_actor.publish_activity(activity)


@when('"{alice}" undoes the interaction the ActivityPub object')
async def alice_undoes(context, alice):
    """Alice undoes the last interaction with the object given by
    [alice_fetches_the_activity_pub_object][cattle_grid.testing.features.steps.fetch.alice_fetches_the_activity_pub_object]
    """
    alice_actor = context.actors[alice]

    activity = (
        alice_actor.activity_factory.undo(
            context.interaction_id,
            to={context.fetch_response.get("attributedTo")},
        )
        .as_public()
        .build()
    )

    await alice_actor.publish_activity(activity)


@given('"{alice}" liked the ActivityPub object')
def alice_liked(context, alice):
    """alias for

    ```gherkin
        Given "{alice}" fetches the ActivityPub object
        When "{alice}" likes the ActivityPub object
        Then For "{alice}", the "likes" collection contains "one" element
    ```
    """
    context.execute_steps(f"""
        Given "{alice}" fetches the ActivityPub object
        When "{alice}" likes the ActivityPub object
        Then For "{alice}", the "likes" collection contains "one" element
""")


@when('"{alice}" announces the ActivityPub object')
async def alice_shares(context, alice):
    """Sends an announce activity"""
    alice_actor = context.actors[alice]

    activity = (
        alice_actor.activity_factory.announce(
            context.fetch_response.get("id"),
            to={context.fetch_response.get("attributedTo")},
        )
        .as_public()
        .build()
    )

    await alice_actor.publish_activity(activity)


@given('"{alice}" announced the ActivityPub object')
def alice_announced(context, alice):
    """alias for

    ```gherkin
        Given "{alice}" fetches the ActivityPub object
        When "{alice}" announces the ActivityPub object
        Then For "{alice}", the "shares" collection contains "one" element
    ```
    """
    context.execute_steps(f"""
        Given "{alice}" fetches the ActivityPub object
        When "{alice}" announces the ActivityPub object
        Then For "{alice}", the "shares" collection contains "one" element
""")


@when('"{alice}" replies to the ActivityPub object with "{text}"')
async def alice_replies(context, alice, text):
    """Replies with text to the ActivityPub object"""
    alice_actor = context.actors[alice]

    reply = (
        alice_actor.object_factory.reply(context.fetch_response, content=text)
        .as_public()
        .build()
    )
    reply["type"] = "Note"

    await alice_actor.publish_object(reply)


@given('"{alice}" replied to the ActivityPub object')
def alice_replied(context, alice):
    """alias for

    ```gherkin
        Given "{alice}" fetches the ActivityPub object
        When "{alice}" replies to the ActivityPub object with "Nice post!"
        Then For "{alice}", the "replies" collection contains "one" element
    ```
    """
    context.execute_steps(f"""
        Given "{alice}" fetches the ActivityPub object
        When "{alice}" replies to the ActivityPub object with "Nice post!"
        Then For "{alice}", the "replies" collection contains "one" element
""")


@given('"{alice}" replied to the ActivityPub object with "{text}')
def alice_replied_with(context, alice, text):
    """alias for

    ```gherkin
        Given "{alice}" fetches the ActivityPub object
        When "{alice}" replies to the ActivityPub object with "{text}"
        Then For "{alice}", the "replies" collection contains "one" element
    ```
    """
    context.execute_steps(f"""
        Given "{alice}" fetches the ActivityPub object
        When "{alice}" replies to the ActivityPub object with "{text}"
        Then For "{alice}", the "replies" collection contains "one" element
""")


@when('"{alice}" deletes her reply to the ActivityPub object')  # type: ignore
async def alice_deletes_reply(context, alice):
    """Deletes the reply in `context.interaction_id."""
    alice_actor = context.actors[alice]

    activity = (
        alice_actor.activity_factory.delete(
            context.interaction_id,
            to={context.fetch_response.get("attributedTo")},
        )
        .as_public()
        .build()
    )

    await alice_actor.publish_activity(activity)


@when('"{alice}" updates her reply with "{text}"')
async def alice_update_post(context, alice, text):
    """Updates the reply in `context.interaction_id."""
    alice_actor = context.actors[alice]

    reply = (
        alice_actor.object_factory.reply(context.fetch_response, content=text)
        .as_public()
        .build()
    )
    reply["type"] = "Note"

    reply["id"] = context.interaction_id

    activity = alice_actor.activity_factory.update(reply).build()

    await alice_actor.publish_activity(activity)


@when('"{alice}" replies to the reply object with "{text}"')
async def alice_replies_to_reply(context, alice, text):
    alice_actor = context.actors[alice]

    reply = alice_actor.object_factory.note(content=text).as_public().build()
    reply["inReplyTo"] = context.interaction_id
    reply["type"] = "Note"

    await alice_actor.publish_object(reply)
