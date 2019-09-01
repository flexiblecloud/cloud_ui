from abc import abstractmethod

import trio


from ..services.service import Service


class Application(Service):

    def __init__(self, cloud: 'UICloud', cookie: str = None):
        if not cookie:
            super().__init__(cloud)
            self.app_instances = dict()
        else:
            self.cookie = cookie
            self.cloud = cloud

    is_single = True
    resizable = True

    @abstractmethod
    def init__gui__(self):
        pass

    def set_handler(self, handler: 'UIApplication'):
        self.handler = handler
        return self

    def run_instance(self, cookie):
        instance = self.__class__(self.cloud, cookie)
        instance.init__gui__()
        self.app_instances[cookie] = instance
        return instance

    def get_widget(self):
        return self.build()

    @abstractmethod
    def build(self):
        pass
