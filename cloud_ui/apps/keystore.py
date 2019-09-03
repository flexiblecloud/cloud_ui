import trio

import remi.gui as G
from cloud_ui.apps.application import Application

try:
    from cloud_ui.cloudapp import UICloud
except ImportError:
    pass


class KeyStoreApplication(Application):
    cloud: 'UICloud'

    def init__gui__(self):
        self.controls = dict()
        self.vbox_list = G.VBox(width="100%")
        self.hbox_add = G.HBox(width="100%")

        self.edit_new_key = G.TextInput(width="30%")
        self.edit_new_value = G.TextInput(width="30%")
        self.button_add_new = G.Button("add", width=50)
        self.button_add_new.onclick.do(self.a(self.on_add_new))

        self.button_reload = G.Button(u"🗘")
        self.button_reload.onclick.do(self.a(self.reload))

        self.hbox_add.append([self.edit_new_key, self.edit_new_value, self.button_add_new])
        self.cloud.add_background_job(self.update_list)

    def build(self):
        vbox = G.VBox(width="500")
        vbox.append([self.button_reload, self.vbox_list, self.hbox_add])
        return vbox

    async def on_add_new(self, *args):
        key = self.edit_new_key.get_value()
        value = self.edit_new_value.get_value()
        keystore_service: 'Service' = self.cloud.get_service("keystore")
        arguments = dict(key=key, value=value)
        set_value = await keystore_service.request("put", arguments)
        if set_value == arguments:
            await self.update_key(key, value)
            self.notify("successful!")
            self.edit_new_key.set_text("")
            self.edit_new_value.set_text("")

    async def update_list(self, *args):

        keystore_service = self.cloud.get_service("keystore")
        if keystore_service:
            all_elements = await keystore_service.request("all")
            for k, v in all_elements:
                await self.update_key(k, v)

    def make_update_handler(self, button, key, edit_control):
        def wrapper(*args):
            async def wrapper_async(*args):
                new_value = edit_control.get_value()
                service = self.cloud.get_service("keystore")
                await service.request("put", dict(key=key, value=new_value))
                self.notify("updated!")

            self.add_background_job(wrapper_async)
        button.onclick.do(wrapper)

    def make_delete_handler(self, button, key):
        def wrapper(*args):
            async def wrapper_async(*args):
                service = self.cloud.get_service("keystore")
                await service.request("delete", key)
                self.vbox_list.remove_child(self.controls[key]['hbox'])
                # await self.reload()
            self.add_background_job(wrapper_async)
        button.onclick.do(wrapper)

    async def update_key(self, key, value):
        control = self.controls.get(key, None)
        if control:
            if control['value'] != value:
                control['edit_value'].set_text(value)
        else:
            control = dict(
                label_key=G.Label(key, width="40%"),
                value=value,
                edit_value=G.TextInput(value, width="40%"),
                hbox=G.HBox(width="100%"),
                button_update=G.Button(u"🗘"),
                button_delete=G.Button(u"X")
            )
            self.make_update_handler(control['button_update'], key, control['edit_value'])
            self.make_delete_handler(control['button_delete'], key)
            control['hbox'].append([
                control['label_key'],
                control['edit_value'],
                control['button_update'],
                control['button_delete']
            ])
            control['edit_value'].set_text(value)
            self.vbox_list.append(control['hbox'])
            self.controls[key] = control
            await trio.sleep(0)

    async def reload(self, *args):
        self.vbox_list.children.clear()
        self.controls = dict()
        await self.update_list()

    @classmethod
    def get_name(cls):
        return "keystore"

    @classmethod
    def list(self):
        pass

    async def process(self, name: str, arguments: 'Any'):
        pass

