from cloud_ui.cloudapp import UICloud
from .service import Service


class TelegramService(Service):

    async def get_token(self):
        self.cloud: 'UICloud'
        await self.cloud.get_service("keystore").request("get", "telegram#telegram_token")

    @classmethod
    def get_name(cls):
        return "telegram_bot"

    @classmethod
    def list(self):
        pass

    async def process(self, name: str, arguments: 'Any'):
        pass