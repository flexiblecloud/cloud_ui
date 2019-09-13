import random
import time

from cloud_ui.services.service import Service


class TimeLineDataService(Service):

    @classmethod
    def get_name(cls):
        return "btc_price"

    @classmethod
    def list(self):
        return ["get_btc_last", "get_eth_last"]

    async def process(self, name: str, arguments: 'Any'):
        if name == "get_btc_last":

            # GETTING BITCOIN Price

            return dict(time=int(time.time()), last_price=random.randint(10000, 10600))
        elif name == "get_eth_last":
            return dict(time=int(time.time()), last_price=random.randint(3000, 5000))
        else:
            return None
