"""
EEG Line Graph widget for live signal visualization.
Uses Kivy Canvas for smooth real-time plotting (replaces fl_chart).
"""
from collections import deque
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import NumericProperty
import theme


class EegGraph(BoxLayout):
    """
    EEG Graph widget that shows a live line chart.
    Data is added via add_data_point() and auto-scrolls.
    """
    max_data_points = NumericProperty(256)
    min_y = NumericProperty(0)
    max_y = NumericProperty(4095)

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self._data = deque(maxlen=256)

        # Title label
        self._title_label = Label(
            text='Live EEG Signal Check',
            font_size=theme.FONT_BODY_SMALL,
            color=theme.TEXT_SECONDARY,
            size_hint_y=None,
            height=20,
            halign='left',
            valign='middle',
        )
        self._title_label.bind(size=self._title_label.setter('text_size'))
        self.add_widget(self._title_label)

        # Placeholder label (shown when no data)
        self._placeholder = Label(
            text='Waiting for signal...',
            font_size=theme.FONT_BODY_REGULAR,
            color=theme.TEXT_MUTED,
        )
        self.add_widget(self._placeholder)

        # Canvas widget for drawing the graph
        self._graph_canvas = _GraphCanvas(
            data=self._data,
            min_y=self.min_y,
            max_y=self.max_y,
        )
        # Initially hidden; shown when data arrives
        self._graph_canvas.opacity = 0
        self.add_widget(self._graph_canvas)

        # Background
        with self.canvas.before:
            Color(*theme.PANEL_BG)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
            Color(*theme.BORDER_DARK)
            self._border_rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, *args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._border_rect.pos = self.pos
        self._border_rect.size = self.size

    def add_data_point(self, value):
        """Add a new data point to the graph."""
        self._data.append(value)
        if self._placeholder.opacity > 0:
            self._placeholder.opacity = 0
            self._graph_canvas.opacity = 1
        self._graph_canvas.redraw()

    def clear(self):
        """Clear all data points."""
        self._data.clear()
        self._placeholder.opacity = 1
        self._graph_canvas.opacity = 0
        self._graph_canvas.redraw()


class _GraphCanvas(Widget):
    """Internal widget that draws the EEG line on its canvas."""

    def __init__(self, data, min_y=0, max_y=4095, **kwargs):
        super().__init__(**kwargs)
        self._data = data
        self._min_y = min_y
        self._max_y = max_y
        self.bind(size=lambda *a: self.redraw(), pos=lambda *a: self.redraw())

    def redraw(self):
        self.canvas.clear()
        if not self._data or self.width <= 0 or self.height <= 0:
            return

        x0 = self.x + 5
        y0 = self.y + 5
        w = self.width - 10
        h = self.height - 10

        # Draw grid lines
        with self.canvas:
            Color(*theme.BORDER_DARK)
            for i in range(5):
                gy = y0 + (h * i / 4)
                Line(points=[x0, gy, x0 + w, gy], width=1)
            for i in range(9):
                gx = x0 + (w * i / 8)
                Line(points=[gx, y0, gx, y0 + h], width=1)

        # Draw data line
        data_list = list(self._data)
        n = len(data_list)
        if n < 2:
            return

        y_range = self._max_y - self._min_y
        if y_range == 0:
            y_range = 1

        points = []
        for i, val in enumerate(data_list):
            px = x0 + (w * i / (n - 1))
            py = y0 + h * ((val - self._min_y) / y_range)
            py = max(y0, min(y0 + h, py))
            points.extend([px, py])

        with self.canvas:
            Color(*theme.TEAL)
            Line(points=points, width=1.5)


class BandPowerBars(BoxLayout):
    """EEG Band Power horizontal bar display."""

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=4, **kwargs)
        self._bands = ['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma']
        self._bars = {}

        # Title
        title = Label(
            text='EEG BAND POWERS',
            font_size=theme.FONT_BODY_SMALL,
            color=theme.TEXT_SECONDARY,
            size_hint_y=None,
            height=20,
            halign='left',
            valign='middle',
        )
        title.bind(size=title.setter('text_size'))
        self.add_widget(title)

        for band in self._bands:
            row = BoxLayout(size_hint_y=None, height=24, spacing=5)
            lbl = Label(
                text=band,
                font_size=theme.FONT_BODY_SMALL,
                color=theme.TEXT_MUTED,
                size_hint_x=None,
                width=50,
                halign='left',
                valign='middle',
            )
            lbl.bind(size=lbl.setter('text_size'))
            bar = _BarWidget(value=0)
            row.add_widget(lbl)
            row.add_widget(bar)
            self._bars[band] = bar
            self.add_widget(row)

        # Background
        with self.canvas.before:
            Color(*theme.BG_DARK)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def update_values(self, values_dict):
        """Update bar values. values_dict maps band name to 0-1 float."""
        for band, bar in self._bars.items():
            bar.value = values_dict.get(band, 0)


class _BarWidget(Widget):
    """A single horizontal progress bar."""
    value = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(value=self._redraw, size=self._redraw, pos=self._redraw)
        self._redraw()

    def _redraw(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Track
            Color(0.165, 0.165, 0.165, 1)
            Rectangle(pos=self.pos, size=self.size)
            # Fill
            Color(*theme.TEAL)
            fill_w = self.width * max(0, min(1, self.value))
            if fill_w > 0:
                Rectangle(pos=self.pos, size=(fill_w, self.height))
