import queue
from abc import abstractmethod

import trio


class Service(object):

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
    async def request(self, name, arguments):
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
                print(f"SERVICE: {self.get_name()} got new request {str(request)}")
                sender = request['sender']
                name = request['name']
                arguments = request['arguments']
                response = await self.process(name, arguments)

                print(f"SERVICE: {self.get_name()} response {response}")
                await sender.send(response)

    """
    handler of request to service ..
    """
    @abstractmethod
    async def process(self, name: str, arguments: 'Any'):
        pass
