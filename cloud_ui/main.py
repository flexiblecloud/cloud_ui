import logging

from cloud_ui.services.dummy import DummyService
from cloud_ui.apps.dummy import DummyApplication
from remi.aserver import start, HttpRequestParser

from .auth.dirrect import DirrectAuth
from .cloudapp import UICloudApp, UICloud

from cloud_ui.services.keystore import KeyStoreService
from cloud_ui.apps.keystore import KeyStoreApplication


if __name__ == "__main__":

    # logging.basicConfig(level=logging.DEBUG)

    UICloud.services = [DummyService, KeyStoreService]
    UICloud.applications = [DummyApplication, KeyStoreApplication]
    # UICloud.services = [DummyService]
    # UICloud.applications = [DummyApplication]

    auth = DirrectAuth()
    auth.add_user(username="admin", password="password", is_admin=True)
    app = UICloud(UICloudApp, HttpRequestParser, 9052, auth)
    start(app)