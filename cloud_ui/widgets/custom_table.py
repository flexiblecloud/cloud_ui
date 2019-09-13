import math

import trio

from remi import gui as G
from remi.gui import *
from remi.gui import TableWidget


class TableExtendedItem(Widget, G._MixinTextualWidget):
    """item widget for the TableRow."""

    @decorate_constructor_parameter_types([str])
    def __init__(self, child, *args, **kwargs):
        """
        Args:
            text (str):
            kwargs: See Widget.__init__()
        """
        super(TableExtendedItem, self).__init__(*args, **kwargs)
        self.type = 'td'

        if isinstance(child, str):
            self.text = child
        else:
            self.text = ""

        self.child = child
        if isinstance(child, str):
            self.append(G.Label(child))
        else:
            self.append(child)

    def get_text(self):
        return self.text

    def set_text(self, text):
        pass


class ExtendedTable(TableWidget):

    # noinspection PyMethodMayBeStatic
    def is_control(self, child):
        return isinstance(child, (
            G.HBox,
            G.VBox,
            G.Button,
            G.Label,
            G.CheckBoxLabel,
            G.CheckBox
        ))

    def _update_first_row(self):

        if len(self.children) > 0:
            for c_key in self.children['0'].children.keys():
                child = self.children['0'].children[c_key]
                if self.is_control(child):
                    instance = TableExtendedItem(child)
                else:
                    instance = TableItem(child.get_text())

                self.children['0'].children[c_key] = instance
                #here the cells of the first row are overwritten and aren't appended by the standard Table.append
                # method. We have to restore de standard on_click internal listener in order to make it working
                # the Table.on_table_row_click functionality

                if not isinstance(instance, TableExtendedItem):
                    self.children['0'].children[c_key].onclick.connect(
                        self.children['0'].on_row_item_click)

    def set_row_count(self, count):
        """Sets the table row count.

        Args:
            count (int): number of rows
        """
        current_row_count = self.row_count()
        current_column_count = self.column_count()
        if count > current_row_count:
            cl = TableExtendedItem
            for i in range(current_row_count, count):
                tr = TableRow()
                for c in range(0, current_column_count):
                    # tr.append(cl(str(c)), str(c))
                    if self._editable:
                        tr.children[str(c)].onchange.connect(
                            self.on_item_changed, int(i), int(c))
                self.append(tr, str(i))
            self._update_first_row()
        elif count < current_row_count:
            for i in range(count, current_row_count):
                self.remove_child(self.children[str(i)])

    def set_column_count(self, count):
        """Sets the table column count.

        Args:
            count (int): column of rows
        """
        current_row_count = self.row_count()
        current_column_count = self.column_count()
        if count > current_column_count:
            cl = TableExtendedItem
            for r_key in self.children.keys():
                row = self.children[r_key]
                for i in range(current_column_count, count):
                    # row.append(cl(), str(i))
                    if self._editable:
                        row.children[str(i)].onchange.connect(
                            self.on_item_changed, int(r_key), int(i))
            self._update_first_row()
        elif count < current_column_count:
            for row in self.children.values():
                for i in range(count, current_column_count):
                    row.remove_child(row.children[str(i)])
        self._column_count = count


class CustomTable(ExtendedTable):

    ITEMS_PER_PAGE = 10

    def build_title(self):
        title_row = TableRow(width="100%")
        for field_name in ["V"] + self.item_fields + self.actions_names:
            title_row.append(TableItem(field_name))

        self.append(title_row)

    def get_pagination(self):
        pagination_container = G.HBox(width="100%")
        pages = math.ceil(len(self.items) / self.items_per_page)

        pagination_container.append(G.Label(f"TOTAL:{len(self.items)} PAGES:{pages}"))

        def set_page_button_handler(button, page_num):
            button.onclick.do(lambda *args: self.show_page(page_num))

        for page in range(pages):
            button = G.Button(f"<{page}>")
            set_page_button_handler(button, page)
            pagination_container.append(button)
        return pagination_container

    def build(self):
        self.build_title()

        print(f"OFFSET = {offset}, ipp = {self.items_per_page}")

        items_to_show = self.items[offset: offset + self.items_per_page]
        print(f"len items to show = {len(items_to_show)}")

        for index, item in enumerate(items_to_show):
            self.build_item(item, index)

