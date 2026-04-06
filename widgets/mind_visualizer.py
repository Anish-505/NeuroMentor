"""
MindVisualizer widget matching Flutter's MindVisualizer.
Animated orb that moves based on focus level with jitter based on stress.
Uses Kivy Canvas for drawing.
"""
import random
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.clock import Clock
from kivy.properties import (
    BooleanProperty, StringProperty, NumericProperty, ListProperty
)
import theme


class MindVisualizer(Widget):
    """
    Animated mind visualizer with a glowing orb.
    Ball Y position responds to focus_ratio, jitter responds to stress_ratio.
    """
    is_active = BooleanProperty(False)
    state_label = StringProperty('IDLE')
    focus_ratio = NumericProperty(1.0)
    stress_ratio = NumericProperty(1.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ball_y = 0.5
        self._target_y = 0.5
        self._jitter_x = 0
        self._jitter_y = 0
        self._jitter_intensity = 0.0
        self._ball_color = list(theme.TEAL)

        # Start animation loop at ~60fps
        self._clock_event = Clock.schedule_interval(self._animate, 1.0 / 60.0)

        self.bind(
            focus_ratio=self._update_data,
            stress_ratio=self._update_data,
            state_label=self._update_data,
            size=lambda *a: self._draw(),
            pos=lambda *a: self._draw(),
        )

    def _update_data(self, *args):
        """Recalculate target position and jitter from ratios."""
        f_val = max(0.5, min(2.5, self.focus_ratio))
        self._target_y = 1.0 - ((f_val - 0.5) / 2.0)

        s_val = max(0.5, min(2.0, self.stress_ratio))
        self._jitter_intensity = (s_val - 0.5) * 0.05

        if self.state_label == 'Stressed':
            self._ball_color = list(theme.RED)
        elif self.state_label == 'Focused':
            self._ball_color = list(theme.GOLD)
        else:
            self._ball_color = list(theme.TEAL)

    def _animate(self, dt):
        """Per-frame animation update."""
        # Smooth interpolation
        self._ball_y += (self._target_y - self._ball_y) * 0.05
        self._ball_y = max(0.1, min(0.9, self._ball_y))

        # Apply jitter
        self._jitter_x = (random.random() - 0.5) * self._jitter_intensity
        self._jitter_y = (random.random() - 0.5) * self._jitter_intensity

        self._draw()

    def _draw(self):
        """Redraw the visualizer."""
        self.canvas.clear()
        w = self.width
        h = self.height
        x0 = self.x
        y0 = self.y

        if w <= 0 or h <= 0:
            return

        with self.canvas:
            # Background
            Color(0.02, 0.02, 0.031, 1)  # #050508
            Rectangle(pos=self.pos, size=self.size)

            # Grid
            Color(0.118, 0.118, 0.157, 1)  # #1E1E28
            for gx in range(0, int(w), 60):
                Line(points=[x0 + gx, y0, x0 + gx, y0 + h], width=1)
            for gy in range(0, int(h), 60):
                Line(points=[x0, y0 + gy, x0 + w, y0 + gy], width=1)

            # Ball position
            cx = x0 + w * 0.5 + self._jitter_x * w
            # Kivy Y is bottom-up, so invert
            cy = y0 + h * (1.0 - self._ball_y) + self._jitter_y * h
            cy = max(y0 + 50, min(y0 + h - 50, cy))
            radius = 40

            # Glow (concentric circles with decreasing alpha)
            for i in range(6, 0, -1):
                alpha = 0.06 * i
                Color(self._ball_color[0], self._ball_color[1],
                      self._ball_color[2], alpha)
                gr = radius * (0.5 + i * 0.5)
                Ellipse(pos=(cx - gr, cy - gr), size=(gr * 2, gr * 2))

            # Ball
            Color(*self._ball_color)
            Ellipse(pos=(cx - radius, cy - radius),
                    size=(radius * 2, radius * 2))

        # Status label is drawn separately so it's always on top
        self.canvas.after.clear()
        with self.canvas.after:
            pass  # Text is handled via an overlay Label if needed

    def on_parent(self, *args):
        """Ensure we have a status label overlay."""
        pass

    def __del__(self):
        if hasattr(self, '_clock_event') and self._clock_event:
            self._clock_event.cancel()
