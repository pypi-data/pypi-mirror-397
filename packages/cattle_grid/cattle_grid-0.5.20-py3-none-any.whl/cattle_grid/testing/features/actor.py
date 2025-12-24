import asyncio
import secrets

from bovine.activitystreams import factories_for_actor_object
from dataclasses import dataclass

from almabtrieb import Almabtrieb, ErrorMessageException
from bovine.activitystreams.activity_factory import ActivityFactory
from bovine.activitystreams.object_factory import ObjectFactory


@dataclass
class Actor:
    profile: dict
    connection: Almabtrieb | None = None

    @property
    def id(self) -> str:
        """
        ``` python
        >>> a = Actor(profile={"id": "http://actor.test"})
        >>> a.id
        'http://actor.test'

        ```
        """
        result = self.profile.get("id")
        if not isinstance(result, str):
            raise Exception("Invalid id format for actor")
        return result

    def id_generator(self):
        def gen():
            return self.id + "/" + secrets.token_hex(8)

        return gen

    @property
    def activity_factory(self) -> ActivityFactory:
        activity_factory, _ = factories_for_actor_object(self.profile)
        return activity_factory

    @property
    def object_factory(self) -> ObjectFactory:
        _, object_factory = factories_for_actor_object(self.profile)
        return object_factory

    @property
    def activity_factory_with_id(self) -> ActivityFactory:
        activity_factory, _ = factories_for_actor_object(
            self.profile, id_generator=self.id_generator()
        )
        return activity_factory

    @property
    def object_factory_with_id(self) -> ObjectFactory:
        _, object_factory = factories_for_actor_object(
            self.profile, id_generator=self.id_generator()
        )
        return object_factory

    async def fetch(self, uri: str, sleep_before: float = 0.1):
        """Fetches an object"""
        await asyncio.sleep(sleep_before)

        if not self.connection:
            raise Exception("Tried to fetch with connectionless actor")

        try:
            data = await self.connection.fetch(self.id, uri)

            assert data.uri == uri

            return data.data
        except ErrorMessageException:
            return None

    async def publish(self, method: str, data: dict, timeout: float = 0.3):
        """Publishes a message"""
        if not self.connection:
            raise Exception("Tried to fetch with connectionless actor")

        await self.connection.trigger(method, data)
        await asyncio.sleep(timeout)

    async def publish_activity(self, activity: dict, timeout: float = 0.3):
        """Publishes a message"""
        msg = {"actor": self.id, "data": activity}
        await self.publish("publish_activity", msg, timeout=timeout)

    async def publish_object(self, obj: dict, timeout: float = 0.3):
        """Publishes a message"""
        msg = {"actor": self.id, "data": obj}
        await self.publish("publish_object", msg, timeout=timeout)

    async def send_message(self, activity: dict):
        msg = {"actor": self.id, "data": activity}
        await self.publish("send_message", msg)
