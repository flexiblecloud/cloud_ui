import logging
import types

import math
import trio

from remi import gui as G
from remi.aserver import ATag

from cloud_ui.widgets.custom_table import CustomTable, TableExtendedItem, ExtendedTable
from cloud_ui.components.model_view.model import Model


class CheckboxBinded(G.CheckBox):

    def __init__(self, id: '_Any', change_handler: types.coroutine, checked=False, user_data='', **kwargs):
        super().__init__(checked, user_data, **kwargs)
        self.change_handler = change_handler
        self.id = id
        self.onclick.do(self.on_click)

    def on_click(self, *args):
        new_value = not self.get_value()
        self.set_value(new_value)
        self.change_handler(self.id, new_value)


class View(ExtendedTable):
    ITEMS_PER_PAGE = 10

    model: Model = None

    add_background_job: types.coroutine = None
    notify: types.coroutine = None

    fields = []

    def __init__(self, add_background_job_afn: types.coroutine, notify_afn: types.coroutine, n_rows, n_columns, use_title=True, editable=False, *args, **kwargs):
        self.model_instance: Model = None
        self.logger = logging.getLogger(f"[View:{self.model_instance}]")
        self.logger.debug("initing ...")
        super().__init__(n_rows, n_columns, use_title, editable, *args, **kwargs)
        self.logger.debug(f"style = {self.style}, type={self.type}")
        self.add_background_job = add_background_job_afn
        if self.model is not None:
            self.set_model(self.model)
        self.label = G.Label(f"[{self.model_instance.__class__}]")
        self.page = 1
        self.selected = set()
        self.shema = None
        self.fields_types = dict()
        self.style['font-size'] = '9px'
        self.style['margin'] = '10px'
        self.notify = notify_afn

    async def refresh_page_internals(self):
        self.logger.debug("C refresh_page_internals")
        self.selected = set()

    def on_change_element_selection(self, element_id, selection_state):
        self.logger.debug(f"selected {element_id} ? {selection_state}")
        if selection_state is False:
            self.selected.remove(element_id)
        else:
            self.selected.add(element_id)

    def make_selection_checkbox(self, element_id, checked=False):
        return CheckboxBinded(element_id, self.on_change_element_selection, checked=checked)

    async def get_page_elements(self):
        self.logger.debug(f"E get_page_elements")

        start = (self.page - 1) * self.ITEMS_PER_PAGE
        stop = start + self.ITEMS_PER_PAGE
        self.logger.debug(f"start = {start}, stop = {stop}")

        elements = [await self.model_instance.get_by_id(id) for id in self.model_instance.ids[start:stop]]
        self.logger.debug(f"elements = {elements}")

        elements = [await self.get_element(element) for element in elements]
        self.logger.debug(f"elements = {elements}")
        self.logger.debug("F get_page_elements")
        return elements

    def set_model(self, model_or_cls):
        self.logger.debug(f"E set_model")
        if issubclass(model_or_cls, Model):
            self.model_instance = model_or_cls()
            self.logger = logging.getLogger(f"[View:{self.model_instance}]")
        elif isinstance(model_or_cls, Model):
            self.model_instance = model_or_cls
            self.logger = logging.getLogger(f"[View:{self.model_instance}]")
        else:
            raise TypeError(f"{model_or_cls} must to be a subclass of Model or instance of it...")
        self.logger.debug(f"L set_model")

    def build(self):
        self.logger.debug(f"C build")
        self.add_background_job(self.build_async)
        return self

    async def get_element(self, element):
        self.logger.debug(f"E add_element {element}")
        row_id = element[self.model_instance.PK]

        row = G.TableRow(width="100%")
        self.logger.debug("drawing row ....")
        checkbox = self.make_selection_checkbox(row_id)
        row.append(TableExtendedItem(checkbox), str(0))

        for col_index, field_name in enumerate(self.fields):
            col_element = await self.render_field(field_name, element)
            self.logger.debug(f"index = {row_id}{col_index} :{col_element}")
            try:
                row.append(TableExtendedItem(col_element), str(col_index + 1))
                self.logger.debug("APPENDED")
            except ValueError as e:
                self.logger.debug(f"{e} ERR: trying to add as TableExtendedItem")
                row.append(TableExtendedItem(col_element), str(col_index + 1))
        self.logger.debug(f"L add_element")
        self.append(row, row_id)
        # return row

    async def render_field(self, field_name, element):
        renderer = getattr(self, f"render_{field_name}", None)
        if not renderer:
            element_type = self.fields_types.get(field_name, None)
            if element_type:
                renderer = getattr(self, f"render_{element_type.__name__}", None)

        if renderer:
            return await renderer(field_name, element)

    async def render_int(self, field_name, element):
        return G.Label(str(element[field_name]))

    async def render_str(self, field_name, element):
        return G.Label(element[field_name])

    async def render_float(self, field_name, element):
        return G.Label(element[field_name])

    _general_renderers = {
        int: render_int,
        str: render_str,
        float: render_float,
    }

    async def prepare_fields(self):
        self.logger.debug(f"E prepare_fields")
        shema = await self.model_instance.fetch_schema()
        self.fields_types = {item['name']: item['type'] for item in shema}

        if len(self.fields) == 0:
            for shema_item in shema:
                self.fields.append(shema_item['name'])
        self.logger.debug(f"L prepare_fields")

    async def build_title(self):
        row = G.TableRow(width="100%")

        checkbox_all = G.CheckBox(checked=False)
        row.append(TableExtendedItem(checkbox_all, width="20px"), str(0))

        for index, field_name in enumerate(self.fields):
            style_args = dict()
            width = getattr(self, f"WIDTH_{field_name}", None)
            if width:
                style_args['width'] = width

            row.append(TableExtendedItem(G.Label(field_name), **style_args), str(index + 1))

        self.append(row, "title_{0}")

    async def build_status(self):
        row = G.TableRow(width="100%")
        td = TableExtendedItem(G.Label(f"{self.model_instance.TABLE_NAME}"))
        td.attributes['colspan'] = str(len(self.fields) + 1)
        row.append(td)
        self.append(row, "status_0")

    async def get_min_page(self):
        return 1

    async def get_max_page(self):
        l = await self.model_instance.get_count()
        pages = int(math.ceil(float(l) / self.ITEMS_PER_PAGE))
        return pages

    def make_move_handler_to_page(self, page):
        def wrapper(*args):
            if self.page != page:
                self.page = page
                self.build()
        return wrapper

    def make_pagination_controls(self, cur_page, min_page, max_page):

        first_page = G.Button("<<")
        if cur_page > min_page:
            first_page.onclick.do(self.make_move_handler_to_page(min_page))
        else:
            first_page.set_enabled(False)

        previous_page = G.Button("<")
        if cur_page > min_page:
            previous_page.onclick.do(self.make_move_handler_to_page(cur_page - 1))
        else:
            previous_page.set_enabled(False)

        last_page = G.Button(">>")
        if max_page > cur_page:
            last_page.onclick.do(self.make_move_handler_to_page(max_page))
        else:
            last_page.set_enabled(False)

        next_page = G.Button(">")
        if max_page > cur_page:
            next_page.onclick.do(self.make_move_handler_to_page(cur_page + 1))
        else:
            next_page.set_enabled(False)

        current_page_info = G.Label(f"{cur_page}")

        return [first_page, previous_page, current_page_info, next_page, last_page]

    async def build_pagination(self):
        row = G.TableRow(width="100%")

        min_page = await self.get_min_page()
        max_page = await self.get_max_page()

        cur_page = self.page

        buttons = self.make_pagination_controls(cur_page, min_page, max_page)

        td = TableExtendedItem(G.HBox([buttons], width="100%"))

        td.attributes['colspan'] = str(len(self.fields) + 1)
        row.append(td)
        self.append(row, "pagination_0")

    async def build_filters(self):
        pass

    async def build_async(self, *args):
        self.empty()
        await self.model_instance.fetch()
        self.logger.debug(f"E build_async")
        await self.prepare_fields()

        self.set_column_count(len(self.fields) + 1)
        await self.build_status()
        await self.build_title()
        await self.build_filters()

        # self.set_row_count(self.ITEMS_PER_PAGE + 1)
        # for element in (await self.get_page_elements()):
        #     print(element)
        #     self.append(element)
        await self.get_page_elements()
        await self.build_pagination()
        self.logger.debug(f"L build_async")
        self.redraw()

