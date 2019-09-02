from remi import gui
from cloud_ui.apps.application import Application
from cloud_ui.services.service import Service


class SimpleService(Service):

    @classmethod
    def get_name(self):
        return "simple-math"

    async def process(self, name, arguments):
        print(f"[{self.get_name()}] processing {name}, {arguments}")
        if name == "mul":
            return self.process_mul(arguments['x'], arguments['y'])
        elif name == "add":
            return self.process_add(arguments['x'], arguments['y'])

    @classmethod
    def list(cls):
        return ["add", "mul"]

    @staticmethod
    def process_mul(x, y):
        return x * y

    @staticmethod
    def process_add(x, y):
        return x + y


class SimpleApplication(Application):

    @classmethod
    def get_name(cls):
        return "dummy"

    def init__gui__(self):
        self.x = gui.TextInput()
        self.y = gui.TextInput()

        self.hbox = hbox = gui.HBox(width="100%")
        hbox.append([
            gui.Label("X = "),
            self.x,
            gui.Label("Y = "),
            self.y
        ])
        self.label = gui.Label(text=f" Result: ")
        self.button = gui.Button("update")
        self.button.onclick.do(self.onclickbutton)

    def build(self):
        vbox = gui.VBox(width="100%")
        vbox.append(self.hbox)
        vbox.append(self.label)
        vbox.append(self.button)
        return vbox

    def onclickbutton(self, event):
        self.server: 'UICloud'
        x = int(self.x.get_text())
        y = int(self.y.get_text())
        service = self.cloud.get_service('simple-math')

        async def onclickbutton(nursery):
            print("sending echo-request to service dummy", service)
            response_add = await service.request("add", dict(x=x, y=y))
            response_mul = await service.request("mul", dict(x=x, y=y))

            self.label.set_text(f" Result: {x} + {y} = {response_add}, {x} * {y} = {response_mul}")
            self.handler.set_need_update()

        print("was sent")
        self.handler.add_foreground_worker(onclickbutton)
