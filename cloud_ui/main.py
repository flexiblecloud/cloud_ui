import logging

from remi.aserver import start, HttpRequestParser

from .auth.dirrect import DirrectAuth
from .cloudapp import UICloudApp, UICloud

from cloud_ui.services.dummy import DummyService
from cloud_ui.apps.dummy import DummyApplication

from cloud_ui.services.keystore import KeyStoreService
from cloud_ui.apps.keystore import KeyStoreApplication

from cloud_ui.services.telegram_notification import TelegramService
from cloud_ui.apps.telegram_notification import TelegramNotificationManageApplication


if __name__ == "__main__":

    # logging.basicConfig(level=logging.DEBUG)

    UICloud.services = [DummyService, KeyStoreService, TelegramService]
    UICloud.applications = [DummyApplication, KeyStoreApplication, TelegramNotificationManageApplication]
    # UICloud.services = [DummyService]
    # UICloud.applications = [DummyApplication]

    auth = DirrectAuth()
    auth.add_user(username="admin", password="password", is_admin=True)
    app = UICloud(UICloudApp, HttpRequestParser, 9052, auth)
    start(app)