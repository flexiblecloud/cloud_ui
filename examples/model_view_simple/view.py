import types

from remi import gui as G
from cloud_ui.components.model_view.view import View

from .model import ExampleModel


class ExampleView(View):
    model = ExampleModel
    WIDTH_name = "120px"
    WIDTH_value = "200px"
    WIDTH_id = "100"

    def __init__(self, add_background_job_afn: types.coroutine, notify_afn: types.coroutine, n_rows, n_columns,
                 use_title=True, editable=False, *args, **kwargs):
        super().__init__(add_background_job_afn, notify_afn, n_rows, n_columns, use_title, editable, *args, **kwargs)
        self.calculated_widgets = dict()

    fields = "id name value count calculated_count".split(" ")

    async def render_calculated_count(self, field_name, element):
        self.logger.debug(f"RENDERING CALCULATED_COUNT WIDGET ... {field_name}:{element}")
        count = element.get('count', 0)

        widget = self.calculated_widgets.get(element.get(self.model_instance.PK))
        if not widget:
            widget = G.Button(f"double {count} ? ")
            self.calculated_widgets[element.get(self.model_instance.PK)] = widget

        def on_double(*args):
            count = element.get('count', 0)
            new_val = count * 2
            element['count'] = new_val
            widget.set_text(f"double {new_val}")
            self.notify(f"new value = {new_val}")

        widget.onclick.do(on_double)
        return widget

