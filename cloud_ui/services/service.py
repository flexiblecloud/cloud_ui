import json
import queue
from abc import abstractmethod
from collections import defaultdict

import trio


class Service(object):

    cloud: 'UICloud'

    """
    return name of service
    """
    @classmethod
    @abstractmethod
    def get_name(cls):
        pass

    def __init__(self, cloud):
        self.cloud = cloud
        self.sender, self.receiver = trio.open_memory_channel(10)
        self.active = True

    """
    list methods-info of the service
    """
    @classmethod
    @abstractmethod
    def list(self):
        return []

    """
    asynchronous request of some method of service ...
    """
    async def request(self, name, arguments=None):
        sender, receiver = trio.open_memory_channel(0)
        await self.sender.send(dict(sender=sender, name=name, arguments=arguments))
        async with receiver:
            async for response in receiver:
                return response

    async def stop(self):
        self.active = False

    """
    main service loop ...
    """
    async def start(self):
        self.active = True
        print(f"SERVICE: {self.get_name()} was started")
        async with self.receiver:
            async for request in self.receiver:
                # print(f"SERVICE: {self.get_name()} got new request {str(request)}")
                sender = request['sender']
                name = request['name']
                arguments = request['arguments']
                response = await self.process(name, arguments)

                # print(f"SERVICE: {self.get_name()} response {response}")
                await sender.send(response)

    """
    handler of request to service ..
    """
    @abstractmethod
    async def process(self, name: str, arguments: 'Any'):
        pass

    async def get_param_keystore(self, param_name, defaultvalue, item=None):
        if item is None:
            item = self.get_name()
        keystore_service = await self.cloud.wait_service("keystore")
        loaded = await keystore_service.request("get", f"{item}#{param_name}")
        if loaded:
            try:
                loaded = json.loads(loaded)
            except Exception as e:
                loaded = None
        if isinstance(defaultvalue, (defaultdict, dict)):
            if loaded:
                try:
                    defaultvalue.update(loaded)
                    return defaultvalue
                except Exception as e:
                    return defaultvalue
            else:
                return defaultvalue
        else:
            return loaded or defaultvalue

    async def save_param_keystore(self, param_name, obj, item=None):
        if item is None:
            item = self.get_name()
        keystore_service = await self.cloud.wait_service("keystore")
        await keystore_service.request("put", dict(key=f"{item}#{param_name}", value=json.dumps(obj)))
