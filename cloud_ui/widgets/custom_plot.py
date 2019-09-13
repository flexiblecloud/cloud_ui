import collections
import io
import threading
import time

import matplotlib.colors
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
# TODO: fix - call as  trio.run_sync_in_thread....
from remi import gui
from remi import gui as G


class CustomPlot(gui.Image):

    ELEMENTS_LIMIT = 10

    def __init__(self, **kwargs):
        super(CustomPlot, self).__init__("/%s/get_image_data?update_index=0" % id(self), **kwargs)
        self._buf = None
        self._buflock = threading.Lock()

        self._fig = Figure(figsize=(4, 4))
        # self.ax = self._fig.add_subplot(111)
        self.storages = collections.defaultdict(list)
        self.xs = collections.defaultdict(list)
        self.axies = collections.defaultdict(lambda *args, **kwargs: self._fig.add_subplot(111))
        self.legends = collections.defaultdict(lambda: False)
        self.redraw()
        self.colors_free = [
            'blue',
            'orange',
            'green',
            'red',
            'purple',
            'brown',
            'pink',
            'gray',
            'olive',
            'cyan',
        ]
        self.colors = collections.defaultdict(lambda : self.colors_free.pop())
        self.items = set()

    def redraw(self):
        canv = FigureCanvasAgg(self._fig)
        buf = io.BytesIO()
        canv.print_figure(buf, format='png')
        with self._buflock:
            if self._buf is not None:
                self._buf.close()
            self._buf = buf

        i = int(time.time() * 1e6)
        self.attributes['src'] = "/%s/get_image_data?update_index=%d" % (id(self), i)

        super(CustomPlot, self).redraw()

    def get_image_data(self, update_index):
        with self._buflock:
            if self._buf is None:
                return None
            self._buf.seek(0)
            data = self._buf.read()

        return [data, {'Content-type': 'image/png'}]

    def set_name(self, name):
        self.axies[name].set_title(name)

    def add_data(self, name, x, data):
        self.items.add(name)
        self.storages[name].append(data)
        self.xs[name].append(x)
        print(self.axies)
        # print(self._fig.subplots())
        ax = self.axies[name]
        # print(f"new data = {name}:{data}, ax id = {id(ax)}")
        ax.plot(
            self.xs[name][-self.ELEMENTS_LIMIT:],
            self.storages[name][-self.ELEMENTS_LIMIT:]
            , label=name, color=self.colors[name])
        if not self.legends[name]:
            ax.legend()
            self.legends[name] = True

    def redraw_all(self):
        self.axies[list(self.items)[0]].clear()
        for name in self.items:
            ax = self.axies[name]

            ax.plot(
                self.xs[name][-self.ELEMENTS_LIMIT:],
                self.storages[name][-self.ELEMENTS_LIMIT:]
                , label=name, color=self.colors[name])
            ax.legend()
        self.redraw()



