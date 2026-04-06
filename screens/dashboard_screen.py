"""
Dashboard screen matching Flutter's DashboardScreen.
Shows welcome title, live status, stat cards, event log, and refresh button.
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from widgets.custom_ui import ShadowButton, GradientCard
from kivy.graphics import Color, Rectangle, RoundedRectangle
import theme


class DashboardScreen(BoxLayout):
    """Dashboard with status overview and event log."""

    def __init__(self, app_state, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=15, **kwargs)
        self._app_state = app_state

        # Welcome title
        self._welcome_lbl = Label(
            text='WELCOME BACK, USER',
            font_size=theme.FONT_TITLE_MEDIUM,
            bold=True,
            color=theme.GOLD,
            size_hint_y=None,
            height=35,
            halign='left',
            valign='middle',
        )
        self._welcome_lbl.bind(size=self._welcome_lbl.setter('text_size'))
        self.add_widget(self._welcome_lbl)

        # Update welcome text when user changes
        app_state.bind(current_user=self._update_welcome)
        self._update_welcome()

        # Live status card
        status_card = GradientCard(
            size_hint_y=None,
            height=80,
            padding=[20, 15]
        )
        status_title = Label(
            text='LIVE STATUS',
            font_size=theme.FONT_BODY_SMALL,
            color=theme.TEXT_SECONDARY,
            size_hint_y=None,
            height=18,
            halign='left',
            valign='middle',
        )
        status_title.bind(size=status_title.setter('text_size'))
        status_card.add_widget(status_title)
        status_value = Label(
            text='OFFLINE',
            font_size=theme.FONT_HEADING_MEDIUM,
            color=theme.TEXT_SECONDARY,
            halign='left',
            valign='middle',
        )
        status_value.bind(size=status_value.setter('text_size'))
        status_card.add_widget(status_value)
        self.add_widget(status_card)

        # Stat cards row
        stats_row = BoxLayout(spacing=15, size_hint_y=None, height=100)
        stats_row.add_widget(self._build_stat_card('STRESS THRESHOLD', 'N/A', theme.RED))
        stats_row.add_widget(self._build_stat_card('FOCUS THRESHOLD', 'N/A', theme.TEAL))
        stats_row.add_widget(self._build_stat_card('NEURO XP', '0', theme.GOLD))
        self.add_widget(stats_row)

        # Event log title
        log_title = Label(
            text='EVENT LOG',
            font_size=theme.FONT_BODY_SMALL,
            color=theme.TEXT_SECONDARY,
            size_hint_y=None,
            height=18,
            halign='left',
            valign='middle',
        )
        log_title.bind(size=log_title.setter('text_size'))
        self.add_widget(log_title)

        # Event log box
        log_box = GradientCard(size_hint_y=0.4, padding=[10, 10])
        log_label = Label(
            text='No events yet',
            font_size=theme.FONT_BODY_REGULAR,
            color=theme.TEAL,
            halign='left',
            valign='top',
        )
        log_label.bind(size=log_label.setter('text_size'))
        log_box.add_widget(log_label)
        self.add_widget(log_box)

        # Refresh button
        refresh_btn = ShadowButton(
            text='SYSTEM REFRESH',
            font_size=theme.FONT_BODY_REGULAR,
            bold=True,
            size_hint_y=None,
            height=45,
            background_color=theme.BUTTON_BG,
            color=theme.GOLD,
        )
        self.add_widget(refresh_btn)

    def _update_welcome(self, *args):
        user = self._app_state.current_user
        name = (user.name.upper() if user and user.name else 'USER')
        self._welcome_lbl.text = f'WELCOME BACK, {name}'

    def _build_stat_card(self, title, value, accent_color):
        card = GradientCard(
            accent_color=accent_color,
            padding=[15, 10]
        )

        t = Label(
            text=title,
            font_size=theme.FONT_BODY_SMALL,
            color=theme.TEXT_MUTED,
            size_hint_y=None,
            height=16,
            halign='left',
            valign='middle',
        )
        t.bind(size=t.setter('text_size'))
        card.add_widget(t)

        v = Label(
            text=value,
            font_size=theme.FONT_HEADING_LARGE,
            bold=True,
            color=accent_color,
            halign='left',
            valign='middle',
        )
        v.bind(size=v.setter('text_size'))
        card.add_widget(v)

        return card
