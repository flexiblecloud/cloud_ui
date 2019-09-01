import trio

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

    def __init__(self, project, **kwargs):
        super(ResizeHelper, self).__init__(**kwargs)
        gui.EventSource.__init__(self)
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

    def __init__(self, project, **kwargs):
        super(DragHelper, self).__init__(**kwargs)
        gui.EventSource.__init__(self)
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


class FloatingPanesContainer(gui.Widget):

    def __init__(self, **kwargs):
        super(FloatingPanesContainer, self).__init__(**kwargs)
        self.resizeHelper = ResizeHelper(self, width=16, height=16)
        self.dragHelper = DragHelper(self, width=15, height=15)
        self.resizeHelper.on_drag.do(self.on_helper_dragged_update_the_latter_pos, self.dragHelper)
        self.dragHelper.on_drag.do(self.on_helper_dragged_update_the_latter_pos, self.resizeHelper)

        self.style['position'] = 'relative'
        self.style['overflow'] = 'auto'

        self.append(self.resizeHelper)
        self.append(self.dragHelper)

    def add_pane(self, pane, x, y):
        pane.style['left'] = gui.to_pix(x)
        pane.style['top'] = gui.to_pix(y)
        pane.onclick.do(self.on_pane_selection)
        pane.style['position'] = 'absolute'
        self.append(pane)
        self.on_pane_selection(pane)

    def on_pane_selection(self, emitter):
        print('on pane selection')
        self.resizeHelper.setup(emitter,self)
        self.dragHelper.setup(emitter,self)
        self.resizeHelper.update_position()
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

    def get_service(self, name):
        service: Service = self.services_instances.get(name, None)
        return service

    def get_application(self, name):
        for application in self.applications:
            if application.get_name() == name:
                return application

    async def start_service(self, service_cls):
        if service_cls.get_name() in self.services_instances:
            return
        service = service_cls(self)
        self.services_instances[service.get_name()] = service

    def list_applications(self):
        return [app.get_name() for app in self.applications]

    def list_services(self):
        return [k for k, v in self.services_instances.items()]

    async def run(self, key_file=None, cert_file=None):
        self.services_instances = dict()
        self.applications = [application_cls(self) for application_cls in self.applications]
        async with trio.open_nursery() as nursery:
            for service_cls in self.services:
                service = service_cls(self)
                self.services_instances[service.get_name()] = service
                nursery.start_soon(service.start)
            for application in self.applications:
                nursery.start_soon(application.start)
            return await super().run(key_file, cert_file)


class UICloudApp(UIApplication):

    def start_application(self, appname):
        application: 'Application' = self.server.get_application(appname)
        application = application.run_instance(self.cookie)
        application.set_handler(self)

        pane = gui.Widget(width=200, height=100)
        pane.style['background-color'] = 'yellow'
        self.floatingPaneContainer.add_pane(pane, 130, 120)
        pane.append(gui.Label(f"[{appname}]"))
        pane.append(application.get_widget())

    def onclick_startdummy(self, *args):
        self.start_application('dummy')

    def main(self):
        button = Button(text="test dummy service")
        button.onclick.do(self.onclick_startdummy)

        self.floatingPaneContainer = FloatingPanesContainer(
            width=1200, height=800, margin='0px auto')
        self.floatingPaneContainer.append(
            gui.Label("Click a panel to select, than drag and stretch"))

        pane1 = gui.Widget(width=200, height=200)
        pane1.style['background-color'] = 'yellow'

        self.floatingPaneContainer.add_pane(pane1, 10, 100)
        pane1.append(gui.Label("Panel1, drag and stretch"))

        pane2 = gui.VBox(width=100, height=200)
        pane2.style['background-color'] = 'green'
        self.floatingPaneContainer.add_pane(pane2, 250, 100)
        pane2.append(gui.Label("Panel2, drag and stretch"))
        pane2.append(button)

        # returning the root widget
        container = VBox(width=300)
        container.append(button)
        return self.floatingPaneContainer
