from remi import gui as G
from cloud_ui.apps.application import Application
from .model import ExampleModel
from .view import ExampleView

ExampleView.model = ExampleModel


class ModelViewExampleApplication(Application):
    width = 400
    height = 400

    def init__gui__(self):
        self.logger.debug("E init__gui__")
        try:
            view = ExampleView(self.add_background_job, self.notify, 10, 10, width="100%", height="400px")
            self.view = view
            self.view.build()
        except Exception as e:
            self.logger(f"ERROR {e}")
        self.logger.debug("L init__gui__")

    def build(self):
        self.logger.debug("E build")
        vbox = G.VBox(width="100%")
        vbox.append(self.view)
        self.logger.debug("L build")
        return vbox


    @classmethod
    def get_name(cls):
        return "model_view_example"