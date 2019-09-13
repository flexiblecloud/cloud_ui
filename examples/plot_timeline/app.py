import trio

import remi.gui as G

from cloud_ui.cloudapp import UICloudApp, UICloud
from cloud_ui.apps.application import Application
from cloud_ui.widgets.custom_plot import CustomPlot


class BitcoinTimelineWatcher(Application):
    session: 'UICloudApp'
    cloud: 'UICloud'

    width = 600
    height = 600

    @classmethod
    def get_name(cls):
        return "btc_watcher"

    def init__gui__(self):
        self.custom_plot = CustomPlot(width="100%", height="100%")
        self.button_start = G.Button("start watching")
        self.button_start.onclick.do(self.on_start_handler)

    def on_start_handler(self, *args):
        self.add_background_job(self.btc_monitor_loop)
        self.button_start.set_enabled(False)

    async def btc_monitor_loop(self, *args):
        btc_monitor_service = await self.cloud.wait_service("btc_price")
        self.active = True
        while self.active:
            await trio.sleep(1)
            new_btc_price_info = await btc_monitor_service.request("get_btc_last")
            new_eth_price_info = await btc_monitor_service.request("get_eth_last")
            # print(f"new price info {new_btc_price_info} and {new_eth_price_info}")
            # print(self.custom_plot.style['width'], self.custom_plot.style['height'])
            if new_btc_price_info and new_eth_price_info:
                self.custom_plot.add_data("btc", new_btc_price_info['time'], new_btc_price_info['last_price'])
                self.custom_plot.add_data("eth", new_eth_price_info['time'], new_eth_price_info['last_price'])
                # self.custom_plot.redraw()
                self.custom_plot.redraw_all()
                self.session.set_need_update()

    def build(self):
        vbox = G.VBox(width="100%")
        vbox.append(self.custom_plot)
        vbox.append(self.button_start)
        return vbox
