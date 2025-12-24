from dataclasses import dataclass, field
from .actor import Actor


@dataclass
class ActivityPubObjects:
    uris: dict = field(default_factory=dict)
    objs: dict = field(default_factory=dict)

    def add_uri(self, name, uri):
        if name in self.uris:
            raise Exception(f"Already uri with name {name} in activitypub uris")
        self.uris[name] = uri

    def add_obj(self, name, obj):
        uri = obj.get("id")
        if name in self.uris:
            raise Exception(f"Already uri with name {name} in activitypub uris")
        self.uris[name] = uri
        self.objs[name] = obj

    async def fetch(self, actor: Actor, name):
        uri = self.uris[name]

        response = await actor.fetch(uri)
        if response is None:
            raise Exception("Failed to fetch object")

        self.objs[name] = response
