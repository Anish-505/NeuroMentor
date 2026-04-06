"""
Monitoring screen matching Flutter's MonitoringScreen.
Live EEG monitoring with Neuro-Game (mind visualizer) and Technical Data tabs.
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from widgets.custom_ui import ShadowButton, GradientCard
from kivy.uix.togglebutton import ToggleButton
from kivy.graphics import Color, RoundedRectangle, Rectangle
import theme
from widgets.mind_visualizer import MindVisualizer
from widgets.eeg_graph import EegGraph, BandPowerBars


class MonitoringScreen(BoxLayout):
    """Live monitoring with tab-like view: Neuro-Game and Technical Data."""

    def __init__(self, app_state, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=15, **kwargs)
        self._app_state = app_state
        self._is_monitoring = False
        self._state_label = 'IDLE'
        self._confidence = 0.0
        self._showing_game = True

        # Tab bar
        tab_row = BoxLayout(size_hint_y=None, height=45, spacing=5)
        with tab_row.canvas.before:
            Color(*theme.BG_DARK)
            tab_row._bg = RoundedRectangle(
                pos=tab_row.pos, size=tab_row.size, radius=[8]
            )
        tab_row.bind(
            pos=lambda inst, val: setattr(inst._bg, 'pos', val),
            size=lambda inst, val: setattr(inst._bg, 'size', val),
        )

        self._tab_game = ToggleButton(
            text='NEURO-GAME',
            group='monitor_tab',
            state='down',
            font_size=theme.FONT_BODY_REGULAR,
            color=theme.GOLD,
        )
        self._tab_game.bind(on_press=lambda *a: self._switch_tab(True))

        self._tab_tech = ToggleButton(
            text='TECHNICAL DATA',
            group='monitor_tab',
            state='normal',
            font_size=theme.FONT_BODY_REGULAR,
            color=theme.TEXT_MUTED,
        )
        self._tab_tech.bind(on_press=lambda *a: self._switch_tab(False))

        tab_row.add_widget(self._tab_game)
        tab_row.add_widget(self._tab_tech)
        self.add_widget(tab_row)

        # Content area
        self._content_area = BoxLayout()
        self.add_widget(self._content_area)

        # Build both views
        self._game_view = self._build_game_view()
        self._tech_view = self._build_tech_view()

        # Show game view by default
        self._content_area.add_widget(self._game_view)

        # Control button
        self._control_btn = ShadowButton(
            text='INITIATE LIVE STREAM',
            font_size=theme.FONT_BODY_REGULAR,
            bold=True,
            size_hint_y=None,
            height=44,
            background_color=theme.BUTTON_BG,
            color=theme.GOLD,
        )
        self._control_btn.bind(on_press=lambda *a: self._toggle_monitoring())
        self.add_widget(self._control_btn)

    def _build_game_view(self):
        view = MindVisualizer(
            is_active=False,
            state_label='IDLE',
        )
        return view

    def _build_tech_view(self):
        view = BoxLayout(orientation='vertical', spacing=10)

        # State display
        state_box = GradientCard(
            size_hint_y=None,
            height=120,
            padding=[20, 20]
        )

        self._state_display = Label(
            text='IDLE',
            font_size=theme.FONT_DISPLAY_LARGE,
            bold=True,
            color=theme.TEXT_MUTED,
        )
        state_box.add_widget(self._state_display)

        conf_row = BoxLayout(size_hint_y=None, height=20)
        self._conf_lbl = Label(
            text='CONF: 0%',
            font_size=theme.FONT_BODY_SMALL,
            color=theme.TEXT_MUTED,
        )
        ver_lbl = Label(
            text='VER: ---',
            font_size=theme.FONT_BODY_SMALL,
            color=theme.TEXT_MUTED,
        )
        conf_row.add_widget(self._conf_lbl)
        conf_row.add_widget(ver_lbl)
        state_box.add_widget(conf_row)
        view.add_widget(state_box)

        # EEG Graph
        self._tech_eeg = EegGraph()
        view.add_widget(self._tech_eeg)

        # Band power bars
        self._band_bars = BandPowerBars(size_hint_y=None, height=160)
        view.add_widget(self._band_bars)

        return view

    def _switch_tab(self, show_game):
        if self._showing_game == show_game:
            return
        self._showing_game = show_game
        self._content_area.clear_widgets()
        if show_game:
            self._content_area.add_widget(self._game_view)
        else:
            self._content_area.add_widget(self._tech_view)

    def _toggle_monitoring(self):
        self._is_monitoring = not self._is_monitoring
        self._game_view.is_active = self._is_monitoring

        if self._is_monitoring:
            self._control_btn.text = 'TERMINATE STREAM'
            self._control_btn.color = theme.RED
            self._control_btn.background_color = theme.DANGER_BUTTON_BG
        else:
            self._control_btn.text = 'INITIATE LIVE STREAM'
            self._control_btn.color = theme.GOLD
            self._control_btn.background_color = theme.BUTTON_BG
            self._state_label = 'IDLE'
            self._confidence = 0.0
            self._state_display.text = 'IDLE'
            self._state_display.color = theme.TEXT_MUTED
            self._conf_lbl.text = 'CONF: 0%'
