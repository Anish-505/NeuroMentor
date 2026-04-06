"""
Breathing task widget matching Flutter's BreathingWidget.
Supports 4-7-8 (Calm) and Box (Focus) breathing modes.
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle
import theme
from widgets.custom_ui import ShadowButton


class BreathingWidget(BoxLayout):
    """Breathing exercise task with modes and score tracking."""

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10, **kwargs)
        self._step = 0
        self._score = 0
        self._is_running = False
        self._mode = '4-7-8'
        self._clock_event = None

        # Instruction label
        self._instruction_lbl = Label(
            text='Ready',
            font_size=40,
            color=theme.TEAL,
            bold=True,
            size_hint_y=0.4,
        )
        self.add_widget(self._instruction_lbl)

        # Mode selector row
        mode_row = BoxLayout(
            size_hint_y=None, height=40,
            spacing=20, padding=[0, 0, 0, 0]
        )
        mode_row.size_hint_x = None
        mode_row.width = 320
        mode_row.pos_hint = {'center_x': 0.5}

        self._btn_478 = ToggleButton(
            text='4-7-8 (Calm)',
            group='breathing_mode',
            state='down',
            font_size=theme.FONT_BODY_REGULAR,
            background_color=theme.GOLD,
            color=theme.BG_DARK,
        )
        self._btn_478.bind(on_press=lambda *a: self.set_mode('4-7-8'))

        self._btn_box = ToggleButton(
            text='Box (Focus)',
            group='breathing_mode',
            state='normal',
            font_size=theme.FONT_BODY_REGULAR,
            background_color=theme.BORDER_DARK,
            color=theme.TEXT_PRIMARY,
        )
        self._btn_box.bind(on_press=lambda *a: self.set_mode('box'))

        mode_row.add_widget(self._btn_478)
        mode_row.add_widget(self._btn_box)
        self.add_widget(mode_row)

        # Score label
        self._score_lbl = Label(
            text='Score: 0',
            font_size=theme.FONT_HEADING_MEDIUM,
            color=theme.GOLD,
            size_hint_y=None,
            height=40,
        )
        self.add_widget(self._score_lbl)

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
        self._mode = mode
        if mode == '4-7-8':
            self._btn_478.state = 'down'
            self._btn_box.state = 'normal'
            self._btn_478.background_color = theme.GOLD
            self._btn_478.color = theme.BG_DARK
            self._btn_box.background_color = theme.BORDER_DARK
            self._btn_box.color = theme.TEXT_PRIMARY
        elif mode == 'box':
            self._btn_box.state = 'down'
            self._btn_478.state = 'normal'
            self._btn_box.background_color = theme.GOLD
            self._btn_box.color = theme.BG_DARK
            self._btn_478.background_color = theme.BORDER_DARK
            self._btn_478.color = theme.TEXT_PRIMARY
            
    def start_task(self):
        self._start()

    def _toggle(self, *args):
        if self._is_running:
            self.stop()
        else:
            self._start()

    def _start(self):
        if self._is_running:
            return
        self._is_running = True
        self._step = 0
        self._score = 0
        self._start_btn.text = 'STOP'
        self._start_btn.color = theme.RED
        self._start_btn.bg_color = theme.DANGER_BUTTON_BG
        self._clock_event = Clock.schedule_interval(self._tick, 1.0)

    def stop(self):
        if self._clock_event:
            self._clock_event.cancel()
            self._clock_event = None
        self._is_running = False
        self._instruction_lbl.text = 'Relax'
        self._start_btn.text = 'START'
        self._start_btn.color = theme.GOLD
        self._start_btn.bg_color = theme.BUTTON_BG

    def _tick(self, dt):
        self._step += 1
        self._score = self._step * 10
        self._score_lbl.text = f'Score: {self._score}'

        cycle_length = 16 if self._mode == 'box' else 19
        curr = self._step % cycle_length

        if self._mode == 'box':
            if curr < 4:
                self._instruction_lbl.text = f'INHALE ({4 - curr})'
            elif curr < 8:
                self._instruction_lbl.text = f'HOLD ({8 - curr})'
            elif curr < 12:
                self._instruction_lbl.text = f'EXHALE ({12 - curr})'
            else:
                self._instruction_lbl.text = f'HOLD ({16 - curr})'
        else:
            if curr < 4:
                self._instruction_lbl.text = f'INHALE ({4 - curr})'
            elif curr < 11:
                self._instruction_lbl.text = f'HOLD ({11 - curr})'
            else:
                self._instruction_lbl.text = f'EXHALE ({19 - curr})'

    def cleanup(self):
        """Call when removing widget to stop timers."""
        if self._clock_event:
            self._clock_event.cancel()
