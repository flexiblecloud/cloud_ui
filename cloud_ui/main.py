from cloud_ui.services.dummy import DummyService
from cloud_ui.apps.dummy import DummyApplication
from remi.aserver import start, HttpRequestParser

from .auth.dirrect import DirrectAuth
from .cloudapp import UICloudApp, UICloud


if __name__ == "__main__":

    UICloud.services = [DummyService]
    UICloud.applications = [DummyApplication]

    auth = DirrectAuth()
    auth.add_user(username="admin", password="password", is_admin=True)
    app = UICloud(UICloudApp, HttpRequestParser, 9052, auth)
    start(app)