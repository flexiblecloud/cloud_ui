from cloud_ui.services.dummy import DummyService
from cloud_ui.apps.dummy import DummyApplication
from remi.aserver import start, HttpRequestParser

from cloud_ui.auth.dirrect import DirrectAuth
from cloud_ui.cloudapp import UICloudApp, UICloud


from .service import TimeLineDataService
from .app import BitcoinTimelineWatcher


def main():
    UICloud.services = [TimeLineDataService]
    UICloud.applications = [BitcoinTimelineWatcher]

    auth = DirrectAuth()
    auth.add_user(username="admin", password="password", is_admin=True)
    app = UICloud(UICloudApp, HttpRequestParser, 9052, auth)
    start(app)


if __name__ == "__main__":
    main()
