"""
Calibration screen matching Flutter's CalibrationScreen.
Contains EEG graph, task cards (baseline/stress/focus), and active task display.
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.clock import Clock
import theme
from widgets.eeg_graph import EegGraph
from widgets.tasks.breathing_widget import BreathingWidget
from widgets.tasks.stroop_widget import StroopWidget
from widgets.tasks.focus_widget import FocusWidget
from widgets.custom_ui import ShadowButton, GradientCard


class CalibrationScreen(BoxLayout):
    """Calibration module with EEG graph, task selector, and active task display."""

    def __init__(self, app_state, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self._app_state = app_state
        self._active_task = None
        self._active_widget = None
        self._sequence_running = False
        self._sequence = []
        self._sequence_idx = 0
        self._time_left = 0
        self._seq_clock = None
        self._manual_clock = None
        self._manual_time = 0
        self._was_running = False

        # EEG Graph (top)
        self._eeg_graph = EegGraph(size_hint_y=None, height=160)
        self.add_widget(self._eeg_graph)

        # Feedback label
        self._feedback_box = BoxLayout(
            size_hint_y=None, height=40, padding=[20, 5],
        )
        with self._feedback_box.canvas.before:
            Color(0, 0, 0, 1)
            self._feedback_box._bg = Rectangle(
                pos=self._feedback_box.pos, size=self._feedback_box.size
            )
        self._feedback_box.bind(
            pos=lambda inst, val: setattr(inst._bg, 'pos', val),
            size=lambda inst, val: setattr(inst._bg, 'size', val),
        )
        self._feedback_lbl = Label(
            text='Waiting for signal...',
            font_size=theme.FONT_BODY_LARGE,
            color=theme.TEXT_MUTED,
            halign='center',
            valign='middle',
        )
        self._feedback_lbl.bind(size=self._feedback_lbl.setter('text_size'))
        self._feedback_box.add_widget(self._feedback_lbl)
        self.add_widget(self._feedback_box)

        # Content area (task cards or active task)
        self._content_area = BoxLayout(padding=[20, 10])
        self.add_widget(self._content_area)
        self._show_task_cards()

        # Execute Sequence Button
        self._seq_btn_box = BoxLayout(size_hint_y=None, height=60, padding=[20, 10])
        self._execute_btn = ShadowButton(
            text='EXECUTE FULL SEQUENCE (1 HOUR)',
            font_size=theme.FONT_BODY_LARGE,
            bold=True,
            background_color=theme.GOLD,
            color=theme.BG_DARK,
        )
        self._execute_btn.bind(on_press=lambda *a: self._start_sequence())
        self._seq_btn_box.add_widget(self._execute_btn)
        self.add_widget(self._seq_btn_box)

        # Control bar
        control_bar = GradientCard(
            orientation='horizontal',
            size_hint_y=None, height=50, padding=[15, 5], spacing=10,
        )

        self._status_lbl = Label(
            text='STATUS: IDLE',
            font_size=theme.FONT_BODY_SMALL,
            color=theme.TEXT_SECONDARY,
            size_hint_x=0.3,
            halign='left',
            valign='middle',
        )
        self._status_lbl.bind(size=self._status_lbl.setter('text_size'))
        control_bar.add_widget(self._status_lbl)

        xp_lbl = Label(
            text='NEURO XP: 0',
            font_size=theme.FONT_HEADING_MEDIUM,
            bold=True,
            color=theme.GOLD,
            size_hint_x=0.25,
        )
        control_bar.add_widget(xp_lbl)

        self._timer_lbl = Label(
            text='00:00',
            font_size=theme.FONT_TIMER,
            bold=True,
            color=theme.TEAL,
            size_hint_x=0.15,
        )
        control_bar.add_widget(self._timer_lbl)

        self._abort_btn = ShadowButton(
            text='ABORT',
            font_size=theme.FONT_BODY_REGULAR,
            bold=True,
            size_hint_x=0.3,
            background_color=theme.DANGER_BUTTON_BG,
            color=theme.RED,
            disabled=True,
        )
        self._abort_btn.bind(on_press=lambda *a: self._stop_task())
        control_bar.add_widget(self._abort_btn)
        self.add_widget(control_bar)

    def _show_task_cards(self):
        self._content_area.clear_widgets()
        cards_row = BoxLayout(spacing=15)

        cards_row.add_widget(self._build_task_card(
            'BASELINE', 'Relaxation', 'Breathing Exercises',
            theme.GOLD, 'baseline'
        ))
        cards_row.add_widget(self._build_task_card(
            'STRESS', 'High Load', 'Math / Stroop',
            theme.RED, 'stress'
        ))
        cards_row.add_widget(self._build_task_card(
            'FOCUS', 'Flow State', 'Tracking / Reading',
            theme.TEAL, 'focus'
        ))
        self._content_area.add_widget(cards_row)

    def _build_task_card(self, title, subtitle, desc, accent, task_id):
        card = GradientCard(padding=[15, 15], spacing=5)

        t = Label(
            text=title,
            font_size=theme.FONT_HEADING_MEDIUM,
            bold=True,
            color=theme.GOLD,
            size_hint_y=None,
            height=25,
            halign='left',
            valign='middle',
        )
        t.bind(size=t.setter('text_size'))
        card.add_widget(t)

        s = Label(
            text=subtitle,
            font_size=theme.FONT_BODY_SMALL,
            italic=True,
            color=theme.TEXT_MUTED,
            size_hint_y=None,
            height=18,
            halign='left',
            valign='middle',
        )
        s.bind(size=s.setter('text_size'))
        card.add_widget(s)

        d = Label(
            text=desc,
            font_size=theme.FONT_BODY_REGULAR,
            color=theme.TEXT_SECONDARY,
            size_hint_y=None,
            height=20,
            halign='left',
            valign='middle',
        )
        d.bind(size=d.setter('text_size'))
        card.add_widget(d)

        # Spacer
        card.add_widget(Label())

        # Spacer
        card.add_widget(Label())

        btn = ShadowButton(
            text='INITIALIZE',
            font_size=theme.FONT_BODY_REGULAR,
            bold=True,
            size_hint_y=None,
            height=40,
            background_color=theme.BUTTON_BG,
            color=theme.GOLD,
        )
        btn.bind(on_press=lambda *a, tid=task_id: self._start_task(tid))
        card.add_widget(btn)

        return card

    def _start_task(self, task_id):
        self._active_task = task_id
        self._status_lbl.text = f'STATUS: {task_id.upper()}'
        self._abort_btn.disabled = False
        self._execute_btn.disabled = True

        self._content_area.clear_widgets()

        task_container = GradientCard(padding=[10, 10])

        if task_id == 'baseline':
            self._active_widget = BreathingWidget()
        elif task_id == 'stress':
            self._active_widget = StroopWidget()
        elif task_id == 'focus':
            self._active_widget = FocusWidget()

        if self._active_widget:
            task_container.add_widget(self._active_widget)
        self._content_area.add_widget(task_container)

        self._manual_time = 0
        self._was_running = False
        if self._manual_clock:
            self._manual_clock.cancel()
        self._manual_clock = Clock.schedule_interval(self._manual_tick, 1.0)
        self._timer_lbl.text = '00:00'

    def _manual_tick(self, dt):
        if self._sequence_running:
            return

        is_running = getattr(self._active_widget, '_is_running', False)
        
        if is_running and not self._was_running:
            self._manual_time = 0
            self._was_running = True
        elif not is_running and self._was_running:
            self._was_running = False
            
        if is_running:
            self._manual_time += 1
            mins = self._manual_time // 60
            secs = self._manual_time % 60
            self._timer_lbl.text = f'{mins:02d}:{secs:02d}'

    def _start_sequence(self):
        self._sequence = [
            ('baseline', '4-7-8'),
            ('baseline', 'box'),
            ('focus', 'tracking'),
            ('focus', 'reading'),
            ('stress', 'stroop'),
            ('stress', 'math')
        ]
        self._sequence_idx = 0
        self._sequence_running = True
        self._run_next_in_sequence()

    def _run_next_in_sequence(self):
        if self._sequence_idx >= len(self._sequence):
            self._stop_task()
            return

        task_id, mode = self._sequence[self._sequence_idx]
        self._start_task(task_id)
        
        if self._active_widget and hasattr(self._active_widget, 'set_mode'):
            self._active_widget.set_mode(mode)
            if hasattr(self._active_widget, 'start_task'):
                self._active_widget.start_task()

        self._time_left = 600 # 10 minutes * 60 seconds
        if self._seq_clock:
            self._seq_clock.cancel()
        self._seq_clock = Clock.schedule_interval(self._sequence_tick, 1.0)
        self._update_timer_label()

    def _sequence_tick(self, dt):
        if self._time_left > 0:
            self._time_left -= 1
            self._update_timer_label()
        else:
            if self._active_widget and hasattr(self._active_widget, '_score'):
                mode = getattr(self._active_widget, '_mode', getattr(self._active_widget, '_is_math_mode', ''))
                self._app_state.save_current_user_score(f'{self._active_task}_{mode}', self._active_widget._score)
            
            if self._active_widget and hasattr(self._active_widget, 'stop'):
                self._active_widget.stop()

            self._sequence_idx += 1
            self._run_next_in_sequence()

    def _update_timer_label(self):
        mins = self._time_left // 60
        secs = self._time_left % 60
        self._timer_lbl.text = f'{mins:02d}:{secs:02d}'

    def _stop_task(self):
        if self._seq_clock:
            self._seq_clock.cancel()
            self._seq_clock = None
        if self._manual_clock:
            self._manual_clock.cancel()
            self._manual_clock = None
        self._sequence_running = False
        self._timer_lbl.text = '00:00'

        if self._active_widget and hasattr(self._active_widget, 'cleanup'):
            self._active_widget.cleanup()
        self._active_task = None
        self._active_widget = None
        self._status_lbl.text = 'STATUS: IDLE'
        self._abort_btn.disabled = True
        self._execute_btn.disabled = False
        self._show_task_cards()
