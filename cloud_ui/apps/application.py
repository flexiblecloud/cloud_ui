import logging
from abc import abstractmethod

import trio

from ..services.service import Service


class Application(Service):

    width = 300
    height = 150

    session: 'UICloudApp'
    cloud: 'UICloud'

    def __init__(self, cloud: 'UICloud', session: 'UICloudApp' = None):
        if not session:
            super().__init__(cloud)
            self.app_instances = dict()
            self.logger = logging.getLogger(f"[{self.get_name()}:ROOT]")
        else:
            self.session = session
            self.cloud = cloud
            self.logger = logging.getLogger(f"[{self.get_name()}:{self.session.cookie}]")

    only_admin = False

    is_single = True
    resizable = True

    """
    wraps asynchronous handler into synchronous callback event-handler
    """
    def a(self, handler_async):
        def wrapper(*args):
            async def wrapper_async(*args):
                await handler_async(*args)
            self.session.add_foreground_worker(wrapper_async)
        return wrapper


    """
    adds coroutine executing to background
    """
    def add_background_job(self, job):
        self.session.add_foreground_worker(job)

    """
    show notification
    """
    def notify(self, message):
        self.session.send_notification(f"{self.get_name()}", message=message)

    """
    creates key gui-controls for app
    """
    @abstractmethod
    def init__gui__(self):
        pass

    """
    run instance of application for current session(user)
    """
    def run_instance(self, session: 'UICloudApp'):
        instance = self.__class__(self.cloud, session)
        instance.init__gui__()
        self.app_instances[session.cookie] = instance
        return instance

    """
    returns rebuilded widget
    """
    def get_widget(self):
        return self.build()

    """
    creates a view of application
    """
    @abstractmethod
    def build(self):
        pass
