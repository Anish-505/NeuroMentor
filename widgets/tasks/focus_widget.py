"""
Focus task widget matching Flutter's FocusWidget.
Supports Visual Tracking and Tech Reading modes.
"""
import random
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.clock import Clock
import theme
from widgets.custom_ui import ShadowButton


ARTICLES = [
    'Neuroplasticity is the ability of neural networks in the brain to reorganize '
    'themselves by creating new neural connections throughout life. This allows '
    'neurons to compensate for injury and disease, and to adjust their activities '
    'in response to new situations. Researchers have discovered that neuroplasticity '
    'is not limited to childhood development but continues throughout adult life. '
    'This groundbreaking finding has revolutionized our understanding of brain '
    'function and has led to new therapeutic approaches for treating brain injuries, '
    'learning disabilities, and neurodegenerative diseases. The brain\'s remarkable '
    'ability to adapt and change forms the biological basis for learning new skills '
    'and forming new memories.',

    'Quantum entanglement is a phenomenon where two or more particles become '
    'interconnected in such a way that the quantum state of each particle cannot '
    'be described independently. When particles are entangled, they remain connected '
    'across vast distances, and measuring one particle instantaneously affects the '
    'state of the other. This counterintuitive phenomenon puzzled even Einstein, '
    'who called it \'spooky action at a distance.\' Today, quantum entanglement is '
    'recognized as a fundamental aspect of quantum mechanics and has practical '
    'applications in quantum computing, quantum cryptography, and quantum '
    'teleportation. Scientists continue to explore the implications of entanglement '
    'for our understanding of reality.',

    'In cognitive science, attention is the cognitive process that allows us to '
    'focus on specific information while filtering out irrelevant stimuli. The '
    'human brain receives countless sensory inputs every second, yet we can only '
    'consciously process a fraction of this information. Selective attention '
    'mechanisms help us prioritize important information and maintain focus on '
    'relevant tasks. Research has shown that attention is not a single unified '
    'process but involves multiple neural systems and brain regions. Understanding '
    'attention mechanisms has profound implications for education, workplace '
    'productivity, mental health treatment, and the design of technology interfaces.',
]


class FocusWidget(BoxLayout):
    """Focus task with Visual Tracking and Tech Reading modes."""

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=10, **kwargs)
        self._is_tracking = True
        self._is_running = False

        # Mode selector row
        mode_row = BoxLayout(
            size_hint_y=None, height=40,
            spacing=20,
        )
        mode_row.size_hint_x = None
        mode_row.width = 320
        mode_row.pos_hint = {'center_x': 0.5}

        self._btn_tracking = ToggleButton(
            text='Visual Tracking',
            group='focus_mode',
            state='down',
            font_size=theme.FONT_BODY_REGULAR,
            background_color=theme.GOLD,
            color=theme.BG_DARK,
        )
        self._btn_tracking.bind(on_press=lambda *a: self.set_mode('tracking'))

        self._btn_reading = ToggleButton(
            text='Tech Reading',
            group='focus_mode',
            state='normal',
            font_size=theme.FONT_BODY_REGULAR,
            background_color=theme.BORDER_DARK,
            color=theme.TEXT_PRIMARY,
        )
        self._btn_reading.bind(on_press=lambda *a: self.set_mode('reading'))

        mode_row.add_widget(self._btn_tracking)
        mode_row.add_widget(self._btn_reading)
        self.add_widget(mode_row)

        # Content area
        self._tracking_view = TrackingView()
        self._reading_view = ReadingView()
        self._reading_view.opacity = 0
        self._reading_view.disabled = True

        self._content = FloatLayout()
        self._content.add_widget(self._tracking_view)
        self._content.add_widget(self._reading_view)
        self.add_widget(self._content)

        # Start/Stop button
        self._start_btn = ShadowButton(
            text='START',
            font_size=theme.FONT_BODY_REGULAR,
            bold=True,
            size_hint=(None, None),
            size=(200, 45),
            pos_hint={'center_x': 0.5},
            bg_color=theme.BUTTON_BG,
            color=theme.GOLD,
        )
        self._start_btn.bind(on_press=self._toggle)
        self.add_widget(self._start_btn)

    def set_mode(self, mode):
        is_tracking = (mode == 'tracking')
        self._is_tracking = is_tracking
        if is_tracking:
            self._btn_tracking.state = 'down'
            self._btn_reading.state = 'normal'
            self._btn_tracking.background_color = theme.GOLD
            self._btn_tracking.color = theme.BG_DARK
            self._btn_reading.background_color = theme.BORDER_DARK
            self._btn_reading.color = theme.TEXT_PRIMARY

            self._tracking_view.opacity = 1
            self._tracking_view.disabled = False
            self._reading_view.opacity = 0
            self._reading_view.disabled = True
        else:
            self._btn_reading.state = 'down'
            self._btn_tracking.state = 'normal'
            self._btn_reading.background_color = theme.GOLD
            self._btn_reading.color = theme.BG_DARK
            self._btn_tracking.background_color = theme.BORDER_DARK
            self._btn_tracking.color = theme.TEXT_PRIMARY

            self._tracking_view.opacity = 0
            self._tracking_view.disabled = True
            self._reading_view.opacity = 1
            self._reading_view.disabled = False

    def start_task(self):
        if not self._is_running:
            self._toggle()

    def stop(self):
        if self._is_running:
            self._toggle()

    def _toggle(self, *args):
        self._is_running = not self._is_running
        if self._is_running:
            self._start_btn.text = 'STOP'
            self._start_btn.color = theme.RED
            self._start_btn.bg_color = theme.DANGER_BUTTON_BG
            self._tracking_view.start()
            self._reading_view.new_article()
        else:
            self._start_btn.text = 'START'
            self._start_btn.color = theme.GOLD
            self._start_btn.bg_color = theme.BUTTON_BG
            self._tracking_view.stop()

    def cleanup(self):
        self._tracking_view.stop()


class TrackingView(Widget):
    """Moving orb for visual tracking exercise."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ball_x = 0.5
        self._ball_y = 0.5
        self._clock_event = None
        self.bind(size=self._draw, pos=self._draw)
        self._draw()

    def start(self):
        if self._clock_event:
            self._clock_event.cancel()
        self._clock_event = Clock.schedule_interval(self._move_ball, 1.0 / 30.0)

    def stop(self):
        if self._clock_event:
            self._clock_event.cancel()
            self._clock_event = None

    def _move_ball(self, dt):
        self._ball_x += (random.random() - 0.5) * 0.02
        self._ball_y += (random.random() - 0.5) * 0.02
        self._ball_x = max(0.05, min(0.95, self._ball_x))
        self._ball_y = max(0.05, min(0.95, self._ball_y))
        self._draw()

    def _draw(self, *args):
        self.canvas.clear()
        w = self.width
        h = self.height
        if w <= 0 or h <= 0:
            return

        with self.canvas:
            # Background
            Color(0, 0, 0, 1)
            Rectangle(pos=self.pos, size=self.size)

            # Orb glow
            cx = self.x + self._ball_x * w
            cy = self.y + self._ball_y * h
            for i in range(4, 0, -1):
                alpha = 0.12 * i
                Color(theme.GOLD[0], theme.GOLD[1], theme.GOLD[2], alpha)
                r = 15 + i * 8
                Ellipse(pos=(cx - r, cy - r), size=(r * 2, r * 2))

            # Orb
            Color(*theme.GOLD)
            Ellipse(pos=(cx - 15, cy - 15), size=(30, 30))


class ReadingView(BoxLayout):
    """Tech article reading exercise."""

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=15, spacing=10, **kwargs)

        self._header = Label(
            text='READ CAREFULLY:',
            font_size=theme.FONT_BODY_SMALL,
            color=theme.TEXT_SECONDARY,
            size_hint_y=None,
            height=20,
            halign='left',
            valign='middle',
        )
        self._header.bind(size=self._header.setter('text_size'))
        self.add_widget(self._header)

        scroll = ScrollView()
        self._article_lbl = Label(
            text=random.choice(ARTICLES),
            font_size=theme.FONT_BODY_LARGE,
            color=theme.TEAL,
            markup=False,
            halign='left',
            valign='top',
            size_hint_y=None,
        )
        self._article_lbl.bind(
            texture_size=lambda inst, sz: setattr(inst, 'height', sz[1]),
            width=lambda inst, w: setattr(inst, 'text_size', (w, None)),
        )
        scroll.add_widget(self._article_lbl)
        self.add_widget(scroll)

        # Background
        with self.canvas.before:
            Color(0.067, 0.067, 0.067, 1)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def new_article(self):
        self._article_lbl.text = random.choice(ARTICLES)
