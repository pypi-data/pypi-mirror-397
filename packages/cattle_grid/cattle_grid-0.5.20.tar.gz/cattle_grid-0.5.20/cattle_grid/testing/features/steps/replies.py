from behave_auto_docstring import given, when, then


@given('"{alice}" fetches "{obj_name}"')
@when('"{alice}" fetches "{obj_name}"')
async def alice_fetches_obj_with_name(context, alice, obj_name):
    await context.ap_objects.fetch(context, alice, obj_name)


@then('The "{obj_name}" has a "{collection}" collection')
def obj_has_collection(context, obj_name, collection):
    obj = context.ap_objects.objs[obj_name]

    assert collection in obj, f"Got object {obj}"


@then(
    'For "{alice}", the "{collection}" collection of "{obj_name}" contains "{number}" elements'
)
async def collection_has_x_elements(context, alice, collection, obj_name, number):
    obj = context.ap_objects.objs[obj_name]
    uri = obj.get(collection)

    response = await context[alice].fetch(uri)

    assert response

    items = response.get("items")
    if not items:
        items = response.get("orderedItems")
    assert isinstance(items, list)

    assert len(items) == int(number), f"Got items {items}"


@given('"{alice}" replies to "{name}" with "{text}" as "{reply_name}"')
@when('"{alice}" replies to "{name}" with "{text}" as "{reply_name}"')
async def alice_replies_with_as(context, alice, name, text, reply_name):
    alice_actor = context.actors[alice]

    reply = (
        alice_actor.object_factory.reply(context.ap_objects.objs[name], content=text)
        .as_public()
        .build()
    )
    reply["type"] = "Note"

    await alice_actor.publish_object(reply)

    while candidate := await context.connections[alice].outgoing().next():
        activity = candidate.get("data", {}).get("raw")
        if activity.get("type") == "Create":
            obj = activity.get("object")
            if obj["content"] == text:
                context.ap_objects.add_obj(reply_name, obj)
                return


@given('"{alice}" replied to "{obj_name}" with "{text}" as "{reply}"')
def step_impl(context, alice, obj_name, text, reply):
    context.execute_steps(f"""
Given "{alice}" fetches "{obj_name}"
When "{alice}" replies to "{obj_name}" with "{text}" as "{reply}"
""")


@when('"{alice}" deletes "{reply_name}"')
async def alice_deletes(context, alice, reply_name):
    alice_actor = context.actors[alice]

    delete = (
        alice_actor.activity_factory.delete(
            context.ap_objects.objs[reply_name].get("id")
        )
        .as_public()
        .build()
    )

    await alice_actor.publish_activity(delete)
