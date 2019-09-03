import json

import trio

try:
    from cloud_ui.cloudapp import UICloud
except ImportError:
    pass
from .service import Service


class KeyStoreService(Service):

    filename = "/tmp/keystore.json"
    cloud: 'UICloud'

    async def synchroniser(self, _nursery):
        while self.active:
            await trio.sleep(30)
            await self.synchronise()

    async def synchronise(self):
        async with await trio.open_file(self.filename, "wt") as f:
            await f.write(json.dumps(self.data))

    async def start(self):
        try:
            f = await trio.open_file(self.filename)
            data = await f.read()
            self.data = json.loads(data)
        except Exception as e:
            self.data = dict()
        self.cloud.add_background_job(self.synchroniser)
        return await super().start()

    @classmethod
    def get_name(cls):
        return "keystore"

    @classmethod
    def list(self):
        return ["get", "put", "list", "all", "delete"]

    async def process(self, name: str, arguments: 'Any'):
        return getattr(self, f"handle_{name}", lambda *p, **kw: None)(arguments)

    def handle_delete(self, arguments):
        try:
            del self.data[arguments]
        except Exception as e:
            pass

    def handle_get(self, arguments):
        return self.data.get(arguments)

    def handle_put(self, arguments):
        key = arguments['key']
        value = arguments['value']
        self.data[key] = value
        return arguments

    def handle_list(self, arguments):
        return list(self.data.keys())

    def handle_all(self, arguments):
        return self.data.items()
