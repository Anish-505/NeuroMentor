"""
Stroop/Math task widget matching Flutter's StroopWidget.
Supports Stroop color test and Rapid Math modes.
"""
import random
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.clock import Clock
import theme
from widgets.custom_ui import ShadowButton


class StroopWidget(BoxLayout):
    """Stroop color + rapid math stress task."""

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10, **kwargs)
        self._score = 0
        self._is_running = False
        self._is_math_mode = False
        self._clock_event = None

        # Stroop state
        self._display_word = 'BLUE'
        self._ink_color = (0, 0, 1, 1)
        self._current_ink_name = 'BLUE'

        # Math state
        self._math_answer = 0
        self._math_problem = ''

        self._colors = ['RED', 'BLUE', 'GREEN', 'YELLOW']
        self._color_map = {
            'RED': (1, 0, 0, 1),
            'BLUE': (0, 0, 1, 1),
            'GREEN': (0, 1, 0, 1),
            'YELLOW': (1, 1, 0, 1),
        }

        # Display label (word or math problem)
        self._display_lbl = Label(
            text='BLUE',
            font_size=60,
            bold=True,
            color=(0, 0, 1, 1),
            size_hint_y=0.35,
        )
        self.add_widget(self._display_lbl)

        # Mode selector row
        mode_row = BoxLayout(
            size_hint_y=None, height=40,
            spacing=20
        )
        mode_row.size_hint_x = None
        mode_row.width = 280
        mode_row.pos_hint = {'center_x': 0.5}

        self._btn_stroop = ToggleButton(
            text='Stroop',
            group='stroop_mode',
            state='down',
            font_size=theme.FONT_BODY_REGULAR,
            background_color=theme.GOLD,
            color=theme.BG_DARK,
        )
        self._btn_stroop.bind(on_press=lambda *a: self.set_mode('stroop'))

        self._btn_math = ToggleButton(
            text='Rapid Math',
            group='stroop_mode',
            state='normal',
            font_size=theme.FONT_BODY_REGULAR,
            background_color=theme.BORDER_DARK,
            color=theme.TEXT_PRIMARY,
        )
        self._btn_math.bind(on_press=lambda *a: self.set_mode('math'))

        mode_row.add_widget(self._btn_stroop)
        mode_row.add_widget(self._btn_math)
        self.add_widget(mode_row)

        # Answer area: color buttons for Stroop, text input for Math
        self._stroop_row = BoxLayout(
            size_hint_y=None, height=50,
            spacing=8,
            pos_hint={'center_x': 0.5},
        )
        for c in self._colors:
            btn = Button(
                text=c,
                font_size=12,
                bold=True,
                background_color=self._color_map[c],
                color=(0, 0, 0, 1),
                size_hint_x=None,
                width=80,
            )
            btn.bind(on_press=lambda inst, cn=c: self._check_stroop(cn))
            self._stroop_row.add_widget(btn)
        self.add_widget(self._stroop_row)

        # Math input (hidden by default)
        self._math_row = BoxLayout(
            size_hint=(None, None), size=(300, 45),
            pos_hint={'center_x': 0.5},
            spacing=10
        )
        
        self._math_input = TextInput(
            hint_text='Answer',
            font_size=theme.FONT_HEADING_MEDIUM,
            multiline=False,
            input_filter='int',
            size_hint=(None, 1),
            width=180,
            background_color=theme.INPUT_BG,
            foreground_color=theme.TEXT_PRIMARY,
        )
        self._math_input.bind(on_text_validate=lambda *a: self._check_math())
        
        self._math_submit = ShadowButton(
            text='SUBMIT',
            font_size=theme.FONT_BODY_REGULAR,
            bold=True,
            bg_color=theme.TEAL,
            color=theme.BG_DARK,
            size_hint=(None, 1),
            width=110,
        )
        self._math_submit.bind(on_press=lambda *a: self._check_math())
        
        self._math_row.add_widget(self._math_input)
        self._math_row.add_widget(self._math_submit)
        
        self._math_row.opacity = 0
        self._math_row.disabled = True
        self.add_widget(self._math_row)

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
        is_math = (mode == 'math')
        self._is_math_mode = is_math
        if is_math:
            self._btn_math.state = 'down'
            self._btn_stroop.state = 'normal'
            self._btn_math.background_color = theme.GOLD
            self._btn_math.color = theme.BG_DARK
            self._btn_stroop.background_color = theme.BORDER_DARK
            self._btn_stroop.color = theme.TEXT_PRIMARY

            self._stroop_row.opacity = 0
            self._stroop_row.disabled = True
            self._math_row.opacity = 1
            self._math_row.disabled = False
        else:
            self._btn_stroop.state = 'down'
            self._btn_math.state = 'normal'
            self._btn_stroop.background_color = theme.GOLD
            self._btn_stroop.color = theme.BG_DARK
            self._btn_math.background_color = theme.BORDER_DARK
            self._btn_math.color = theme.TEXT_PRIMARY

            self._stroop_row.opacity = 1
            self._stroop_row.disabled = False
            self._math_row.opacity = 0
            self._math_row.disabled = True
        if self._is_running:
            self._next_round()

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
        self._score = 0
        self._score_lbl.text = 'Score: 0'
        self._start_btn.text = 'STOP'
        self._start_btn.color = theme.RED
        self._start_btn.bg_color = theme.DANGER_BUTTON_BG
        self._next_round()
        self._clock_event = Clock.schedule_interval(
            lambda dt: self._next_round(), 3.0
        )

    def stop(self):
        if self._clock_event:
            self._clock_event.cancel()
            self._clock_event = None
        self._is_running = False
        self._start_btn.text = 'START'
        self._start_btn.color = theme.GOLD
        self._start_btn.bg_color = theme.BUTTON_BG

    def _next_round(self):
        if self._is_math_mode:
            a = random.randint(10, 99)
            b = random.randint(10, 99)
            is_add = random.choice([True, False])
            self._math_answer = a + b if is_add else a - b
            op = '+' if is_add else '-'
            self._math_problem = f'{a} {op} {b} = ?'
            self._display_lbl.text = self._math_problem
            self._display_lbl.color = theme.RED
            self._math_input.text = ''
        else:
            word = random.choice(self._colors)
            ink_name = random.choice(self._colors)
            self._display_word = word
            self._ink_color = self._color_map[ink_name]
            self._current_ink_name = ink_name
            self._display_lbl.text = word
            self._display_lbl.color = self._ink_color

    def _check_stroop(self, color_name):
        if not self._is_running:
            return
        if color_name == self._current_ink_name:
            self._score += 50
            self._score_lbl.text = f'Score: {self._score}'
        # Reset timer
        if self._clock_event:
            self._clock_event.cancel()
        self._next_round()
        self._clock_event = Clock.schedule_interval(
            lambda dt: self._next_round(), 3.0
        )

    def _check_math(self):
        if not self._is_running:
            return
        try:
            answer = int(self._math_input.text)
        except (ValueError, TypeError):
            answer = 0
        if answer == self._math_answer:
            self._score += 50
            self._score_lbl.text = f'Score: {self._score}'
        # Reset timer
        if self._clock_event:
            self._clock_event.cancel()
        self._next_round()
        self._clock_event = Clock.schedule_interval(
            lambda dt: self._next_round(), 3.0
        )

    def cleanup(self):
        """Call when removing widget to stop timers."""
        if self._clock_event:
            self._clock_event.cancel()
