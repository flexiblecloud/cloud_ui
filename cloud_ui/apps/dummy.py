from remi import gui
from .application import Application


class DummyApplication(Application):
    width = 400
    height = 200

    @classmethod
    def get_name(cls):
        return "dummy"

    def init__gui__(self):
        self.text = gui.TextInput()
        self.text.set_text("empty")
        self.label = gui.Label(text=f"INPUTED TEXT: {self.text.get_value()}")
        self.button = gui.Button("update")
        self.button.onclick.do(self.onclickbutton)

    def build(self):
        vbox = gui.VBox(width="200")
        vbox.append(self.label)
        vbox.append(self.text)
        vbox.append(self.button)
        return vbox

    def onclickbutton(self, event):
        self.server: 'UICloud'
        text = self.text.get_text()
        service = self.cloud.get_service('dummy')
        print(f"before send request...{text}")

        async def onclickbutton(nursery):
            print("sending echo-request to service dummy", service)
            response = await service.request("echo", text)
            print(f"got echo-response = {response}")
            self.label.set_text(f"INPUTED TEXT: {self.text.get_value()}")
            self.session.set_need_update()

        print("was sent")
        self.session.add_foreground_worker(onclickbutton)
