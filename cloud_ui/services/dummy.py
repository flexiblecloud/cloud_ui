from .service import Service


class DummyService(Service):

    @classmethod
    def get_name(self):
        return "dummy"

    async def process(self, name, arguments):
        print(f"[{self.get_name()}] processing {name}, {arguments}")
        if name == "echo":
            return arguments

    @classmethod
    def list(self):
        return ["echo"]
