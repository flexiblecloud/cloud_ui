import trio

import remi
import remi.gui as G
from cloud_ui.services.service import Service
from cloud_ui.apps.application import Application
from remi import gui
from remi.gui import (
    VBox, HBox, Label,
    Button,
    Input, TextInput,
    CheckBox, CheckBoxLabel,
    ColorPicker, Date,
    DropDown, DropDownItem,
    TreeView, TreeItem
)

from remi.aserver import AServer, Application as UIApplication, AuthFactory


class ResizeHelper(gui.Widget, gui.EventSource):
    EVENT_ONDRAG = "on_drag"

    def __init__(self, project, parent, **kwargs):
        super(ResizeHelper, self).__init__(**kwargs)
        gui.EventSource.__init__(self)
        self.parent = parent
        self.style['float'] = 'none'
        self.style['background-color'] = "transparent"
        self.style['border'] = '1px dashed black'
        self.style['position'] = 'absolute'
        self.style['left']='0px'
        self.style['top']='0px'
        self.project = project
        self.parent = None
        self.refWidget = None
        self.active = False
        self.onmousedown.do(self.start_drag)

        self.origin_x = -1
        self.origin_y = -1

    def setup(self, refWidget, newParent):
        #refWidget is the target widget that will be resized
        #newParent is the container
        if self.parent:
            try:
                self.parent.remove_child(self)
            except:
                #there was no ResizeHelper placed
                pass
        if newParent==None:
            return
        self.parent = newParent
        self.refWidget = refWidget
        try:
            self.parent.append(self)
        except:
            #the selected widget's parent can't contain a ResizeHelper
            pass
        #self.refWidget.style['position'] = 'relative'
        self.update_position()

    def start_drag(self, emitter, x, y):
        self.active = True
        self.project.onmousemove.do(self.on_drag)
        self.project.onmouseup.do(self.stop_drag)
        self.project.onmouseleave.do(self.stop_drag, 0, 0)
        self.origin_x = -1
        self.origin_y = -1

    def stop_drag(self, emitter, x, y):
        self.active = False
        self.update_position()

    @gui.decorate_event
    def on_drag(self, emitter, x, y):
        if self.active:
            if self.origin_x == -1:
                self.origin_x = float(x)
                self.origin_y = float(y)
                self.refWidget_origin_w = gui.from_pix(self.refWidget.style['width'])
                self.refWidget_origin_h = gui.from_pix(self.refWidget.style['height'])
            else:
                self.refWidget.style['width'] = gui.to_pix(self.refWidget_origin_w + float(x) - self.origin_x )
                self.refWidget.style['height'] = gui.to_pix(self.refWidget_origin_h + float(y) - self.origin_y)
                self.update_position()
            return ()

    def update_position(self):
        self.style['position']='absolute'
        self.style['left']=gui.to_pix(gui.from_pix(self.refWidget.style['left']) + gui.from_pix(self.refWidget.style['width']) - gui.from_pix(self.style['width'])/2)
        self.style['top']=gui.to_pix(gui.from_pix(self.refWidget.style['top']) + gui.from_pix(self.refWidget.style['height']) - gui.from_pix(self.style['height'])/2)


class DragHelper(gui.Widget, gui.EventSource):
    EVENT_ONDRAG = "on_drag"

    def __init__(self, project, parent, **kwargs):
        super(DragHelper, self).__init__(**kwargs)
        gui.EventSource.__init__(self)
        self.parent = parent
        self.style['float'] = 'none'
        self.style['background-color'] = "transparent"
        self.style['border'] = '1px dashed black'
        self.style['position'] = 'absolute'
        self.style['left']='0px'
        self.style['top']='0px'
        self.project = project
        self.parent = None
        self.refWidget = None
        self.active = False
        self.onmousedown.do(self.start_drag)

        self.origin_x = -1
        self.origin_y = -1

    def setup(self, refWidget, newParent):
        #refWidget is the target widget that will be resized
        #newParent is the container
        if self.parent:
            try:
                self.parent.remove_child(self)
            except:
                #there was no ResizeHelper placed
                pass
        if newParent==None:
            return
        self.parent = newParent
        self.refWidget = refWidget
        try:
            self.parent.append(self)
        except:
            #the selected widget's parent can't contain a ResizeHelper
            pass
        #self.refWidget.style['position'] = 'relative'
        self.update_position()

    def start_drag(self, emitter, x, y):
        self.active = True
        self.project.onmousemove.do(self.on_drag)
        self.project.onmouseup.do(self.stop_drag)
        self.project.onmouseleave.do(self.stop_drag, 0, 0)
        self.origin_x = -1
        self.origin_y = -1

    def stop_drag(self, emitter, x, y):
        self.active = False
        self.update_position()

    @gui.decorate_event
    def on_drag(self, emitter, x, y):
        if self.active:
            if self.origin_x == -1:
                self.origin_x = float(x)
                self.origin_y = float(y)
                self.refWidget_origin_x = gui.from_pix(self.refWidget.style['left'])
                self.refWidget_origin_y = gui.from_pix(self.refWidget.style['top'])
            else:
                self.refWidget.style['left'] = gui.to_pix(self.refWidget_origin_x + float(x) - self.origin_x )
                self.refWidget.style['top'] = gui.to_pix(self.refWidget_origin_y + float(y) - self.origin_y)
                self.update_position()
            return ()

    def update_position(self):
        self.style['position']='absolute'
        self.style['left']=gui.to_pix(gui.from_pix(self.refWidget.style['left']) - gui.from_pix(self.style['width'])/2)
        self.style['top']=gui.to_pix(gui.from_pix(self.refWidget.style['top']) - gui.from_pix(self.style['height'])/2)
        # self.parent.try_update()


class FloatingPanesContainer(gui.Widget):

    def __init__(self, parent, **kwargs):
        super(FloatingPanesContainer, self).__init__(**kwargs)
        self.parent = parent
        self.resizeHelper = ResizeHelper(self, parent, width=16, height=16)
        self.dragHelper = DragHelper(self, parent, width=15, height=15)
        self.resizeHelper.on_drag.do(self.on_helper_dragged_update_the_latter_pos, self.dragHelper)
        self.dragHelper.on_drag.do(self.on_helper_dragged_update_the_latter_pos, self.resizeHelper)

        self.style['position'] = 'relative'
        self.style['overflow'] = 'auto'

        self.append(self.resizeHelper)
        self.append(self.dragHelper)

    def add_pane(self, pane, x, y, resizable=True):
        pane.style['left'] = gui.to_pix(x)
        pane.style['top'] = gui.to_pix(y)
        pane.onclick.do(self.on_pane_selection)
        pane.style['position'] = 'absolute'
        pane.resizable = resizable
        self.append(pane)
        self.on_pane_selection(pane)

    def on_pane_selection(self, emitter):
        # print('on pane selection')
        if emitter.resizable:
            self.resizeHelper.setup(emitter,self)
            self.resizeHelper.update_position()
        self.dragHelper.setup(emitter,self)
        self.dragHelper.update_position()

    def on_helper_dragged_update_the_latter_pos(self, emitter, widget_to_update):
        widget_to_update.update_position()


class UICloud(AServer):


    """
    set of available services
    """
    services = []

    """
    set of available applications
    """
    applications = []

    """
    returns running service
    """
    def get_service(self, name):
        service: Service = self.services_instances.get(name, None)
        return service

    """
    returns running application handler
    """
    def get_application(self, name):
        for application in self.applications:
            if application.get_name() == name:
                return application

    """
    starts some service
    """
    async def start_service(self, service_cls):
        if service_cls.get_name() in self.services_instances:
            return
        service = service_cls(self)
        self.services_instances[service.get_name()] = service

    """
    returns list of applications
    """
    def list_applications(self):
        return [app.get_name() for app in self.applications]

    """
    returns list of services
    """
    def list_services(self):
        return [k for k, v in self.services_instances.items()]

    """
    add background job
    """
    def add_background_job(self, job):
        self.nursery.start_soon(job, self.nursery)

    async def run(self, key_file=None, cert_file=None):
        self.services_instances = dict()
        self.applications = [application_cls(self) for application_cls in self.applications]
        async with trio.open_nursery() as nursery:
            self.nursery = nursery
            for service_cls in self.services:
                service = service_cls(self)
                self.services_instances[service.get_name()] = service
                nursery.start_soon(service.start)
            for application in self.applications:
                nursery.start_soon(application.start)
            return await super().run(key_file, cert_file)


class UICloudApp(UIApplication):


    """
    user name
    """
    @property
    def username(self):
        return self.cookie


    """
    session for current user
    """
    @property
    def session(self):
        return self

    """
    wraps asynchronous handler into synchronous callback event-handler
    """
    def a(self, handler_async):
        def wrapper(*args):
            async def wrapper_async(*args):
                await handler_async(*args)
            self.handler: 'UIApplication'
            self.handler.add_foreground_worker(wrapper_async)
        return wrapper

    def try_update(self):
        self.session.set_need_update()
        self.add_background_job(self.update)

    async def update(self, *args):
        await self.session.do_gui_update()

    """
    returns cloud
    """
    @property
    def cloud(self) -> UICloud:
        return self.server

    """
    adds corotine to execute in background
    """
    def add_background_job(self, job):
        self.add_foreground_worker(job)

    add_foreground_job = add_background_job

    """
    """
    def send_notification(self, title, message=None):
        async def wrapper(*args):
            await self.session.notification_message(title=title, content=message if message else "")
        self.add_background_job(wrapper)

    """
    checks if user is admin
    """
    def is_admin(self):
        return self.server.auth_factory.is_admin(self.cookie)

    def build_apps_pannel(self):
        is_admin = self.is_admin()
        self.server: UICloud
        hbox = gui.HBox(width="100%")
        for appname in self.server.list_applications():
            if not is_admin:
                application = self.server.get_application(appname)
                if application.only_admin:
                    continue
            button = gui.Button(appname)

            def make_runner(appname):
                def wrapper(*args):
                    self.start_application(appname)
                return wrapper
            button.onclick.do(make_runner(appname))
            hbox.append(button)
        return hbox

    def build_services_pannel(self):
        self.server: UICloud
        hbox = gui.HBox()
        for service in self.server.services_instances:
            hbox.append(gui.Label(service))
        return hbox

    """
    user api to get run pre-installed application
    """

    def __init__(self, cookie: str, stream: trio.SocketStream, headers: dict, server: 'AServer'):
        super().__init__(cookie, stream, headers, server)
        self.applications_panes = dict()

    def start_application(self, appname):
        application: 'Application' = self.server.get_application(appname)
        application = application.run_instance(self.session)

        pane = G.Widget(width=200, height=100)
        self.prepare_pane(pane, application)
        self.applications_panes[application] = pane
        self.floatingPaneContainer.add_pane(pane, 130, 120, resizable=application.resizable)

        self.update()

    def prepare_pane(self, pane: remi.gui.Widget, application: Application):
        pane.style['background-color'] = 'gray'

        control_panel = G.HBox(width="100%")
        control_panel.style['background-color'] = 'green'
        control_panel.style['align'] = "left"
        control_panel.append(G.Label(f"[{application.get_name()}]"))

        maximize_button = G.Button(u"🗖")
        minimize_button = G.Button(u"🗕")
        stop_button = G.Button(u"❎")

        control_panel.append([minimize_button, maximize_button, stop_button])

        pane.append(control_panel)
        widget = application.get_widget()
        pane.append(widget)

        # self.send_notification("width", message=f"width={widget.style['width']}")

        pane.style['width'] = widget.style['width'].replace('px', '')
        # pane.style['height'] = widget.style['height'].replace('px', '')

        self.make_on_maximize_pane(pane, maximize_button)

    @property
    def width(self):
        return self.floatingPaneContainer.style['width'].replace("px", '')

    @property
    def height(self):
        return self.floatingPaneContainer.style['height'].replace("px", '')

    def make_on_maximize_pane(self, pane, button):
        def wrapper(*args):
            print("getting sizes...")
            try:
                # new_width = int(self.width) / 100.0 * 90
                new_width = "90%"
                # new_heigth = int(float(self.height) / 100.0 * 90)
                new_heigth = "90%"
            except Exception as e:
                print("error:")
                print(e)
                return
            # self.send_notification(f"size", message=f"oh = {self.height}, ow = {self.width}, nh = {new_heigth}, nw = {new_width}")
            print(pane.children)
            for child_key in pane.children:
                pane.children[child_key].style['width'] = "100%"
        button.onclick.do(wrapper)

    def onclick_startdummy(self, *args):
        self.start_application('dummy')

    def main(self):
        button = Button(text="test dummy service")
        button.onclick.do(self.onclick_startdummy)

        container = gui.VBox(width="100%")
        container.append(self.build_services_pannel())

        workspace = gui.HBox(width="100%")
        workspace.style['align'] = "left"
        apps_pannel = self.build_apps_pannel()
        workspace.append(apps_pannel)
        container.append(workspace)

        self.floatingPaneContainer = FloatingPanesContainer(self,
            width="100%", height="100%", margin='0px auto')
        workspace.append(self.floatingPaneContainer)
        self.floatingPaneContainer.append(
            gui.Label("Click a panel to select, than drag and stretch"))

        return container
