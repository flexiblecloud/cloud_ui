import trio

import remi.gui as G
from cloud_ui.apps.application import Application

try:
    from cloud_ui.cloudapp import UICloud
except ImportError:
    pass


class TelegramNotificationManageApplication(Application):
    async def init(self, *args):
        await self.cloud.wait_service("telegram_bot")

    def init__gui__(self):
        self.vbox_list_requests = G.VBox(width="100%")
        self.vbox_list_requests.append(G.Label("[Pending user requests]"))

        self.button_update = G.Button(u"🗘")
        self.button_update.onclick.do(self.a(self.on_update_all))

        self.vbox_publics = G.VBox(width="100%")
        self.vbox_publics.append(G.Label("[Publics]"))

        self.hbox_create_new = G.HBox(width="100%")
        self.edit_name = G.TextInput()
        self.button_add_new = G.Button("+")
        self.hbox_create_new.append([self.edit_name, self.button_add_new])
        self.button_add_new.onclick.do(self.a(self.on_add_new))

        self.vbox_publish_form = G.VBox(width="100%")
        self.select_channels = G.DropDown()
        self.edit_publish =G.TextInput()
        self.button_publish = G.Button("publish")
        self.button_publish.onclick.do(self.a(self.on_publish))
        self.vbox_publish_form.append([
            G.Label("[new publishment]"),
            self.select_channels,
            self.edit_publish,
            self.button_publish
        ])

        self.publics_controls = dict()

    def build(self):
        vbox = G.VBox(width="600")
        vbox.style['align'] = "left"
        vbox.append([self.button_update, self.vbox_list_requests, self.vbox_publics, self.hbox_create_new, self.vbox_publish_form])

        return vbox

    @classmethod
    def get_name(cls):
        return "telegram_notification"

    @classmethod
    def list(self):
        pass

    async def process(self, name: str, arguments: 'Any'):
        pass

    async def on_publish(self, *args):
        text_to_publish = self.edit_publish.get_value()
        self.button_publish.set_enabled(False)
        channel = self.select_channels.get_value()
        self.edit_publish.set_text("")

        service = await self.cloud.wait_service("telegram_bot")
        await service.request("publish", dict(channel=channel, payload=text_to_publish))
        self.notify("published!")
        self.button_publish.set_enabled(True)

    async def on_update_all(self, *args):
        self.select_channels.empty()
        await self.on_update_publics()
        await self.on_update_requests()

    async def on_update_requests(self, *args):
        service = await self.cloud.wait_service("telegram_bot")
        pending_requests = await service.request("list_pending")
        for chat_id in pending_requests:
            await self.show_pending_request(chat_id, pending_requests[chat_id])

    async def on_update_publics(self, *args):
        service = await self.cloud.wait_service("telegram_bot")
        publics = await service.request("list")
        print("publics list gotten:", publics)
        for public in publics:
            await self.show_public(public)

    async def show_pending_request(self, chat_id, info):
        approve_button = G.Button("approve")
        hbox = G.HBox(width="100%")
        hbox.append([
            G.Label(f"{info}", width=150),
            approve_button
        ])
        self.vbox_list_requests.append(hbox)
        self.make_approve_handler(hbox, approve_button, chat_id)

    async def show_public(self, public):
        self.select_channels.append(G.DropDownItem(text=public['name']))

        if public['name'] in self.publics_controls:
            control = self.publics_controls[public['name']]
        else:
            control = dict(
                vbox=G.VBox(width="100%")
            )
            self.vbox_publics.append(control['vbox'])
            self.publics_controls[public['name']] = control

        try:
            subscribers_list_control = control['vbox']
            subscribers_list_control.empty()
            subscribers_list_control.append(G.Label(f"[{public['name']}]: {len(public['subscribers'])}"))
            subscribers = sorted(public['subscribers'])
            for subscriber in subscribers:
                subscribers_list_control.append(G.Label(subscriber))
        except Exception as e:
            pass

    async def on_add_new(self, *args):

        self.button_add_new.set_enabled(False)
        public_name = self.edit_name.get_value()
        print(f"adding new public {public_name}")
        service = await self.cloud.wait_service("telegram_bot")
        await service.request("create", public_name)
        await self.on_update_publics()
        self.edit_name.set_text("")
        self.button_add_new.set_enabled(True)

    def make_approve_handler(self, hbox, approve_button, chat_id):
        def wrapper(*args):
            async def wrapper_async(*args):
                service = await self.cloud.wait_service("telegram_bot")
                await service.request("approve_pending", chat_id)
                self.vbox_list_requests.remove_child(hbox)
            self.add_background_job(wrapper_async)
        approve_button.onclick.do(wrapper)

    cloud: 'UICloud'

