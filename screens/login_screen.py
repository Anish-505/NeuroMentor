"""
Login screen with previous user quick-select tiles and new user input.
"""
import re
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.behaviors import ButtonBehavior
from widgets.custom_ui import ShadowButton, GradientCard
from kivy.graphics import Color, RoundedRectangle, Rectangle, Ellipse
from kivy.metrics import dp, sp
import theme


# Avatar color palette for user tiles
_AVATAR_COLORS = [
    '#2563eb', '#16a34a', '#ea0c0c',
    '#f59e0b', '#7c3aed', '#db2777',
]


class UserTile(ButtonBehavior, Widget):
    """Clickable user avatar tile for quick login."""

    def __init__(self, username, on_select=None, **kwargs):
        self.username = username
        self._on_select = on_select
        kwargs['size_hint'] = (None, None)
        kwargs['size'] = (dp(80), dp(90))
        super().__init__(**kwargs)
        self._pressed = False

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self._draw()

    def _get_avatar_color(self):
        idx = hash(self.username) % len(_AVATAR_COLORS)
        return theme.rgba_hex(_AVATAR_COLORS[idx], 1.0)

    def _draw(self):
        self._update_canvas()

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        self.canvas.after.clear()

        with self.canvas.before:
            # Background rounded rect
            if self._pressed:
                Color(*theme.rgba_hex('#2563eb', 0.4))
            else:
                Color(*theme.rgba_hex('#1a2535', 1.0))
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[12, 12, 12, 12],
            )

            # Avatar circle
            avatar_color = self._get_avatar_color()
            Color(*avatar_color)
            avatar_d = dp(44)
            avatar_x = self.x + (self.width - avatar_d) / 2
            avatar_y = self.y + self.height - avatar_d - dp(8)
            Ellipse(
                pos=(avatar_x, avatar_y),
                size=(avatar_d, avatar_d),
            )

        with self.canvas.after:
            pass  # Labels added as children below

        # Remove old children labels
        self.clear_widgets()

        # Initial letter label (centered on avatar)
        letter = self.username[0].upper() if self.username else '?'
        avatar_d = dp(44)
        avatar_x = self.x + (self.width - avatar_d) / 2
        avatar_y = self.y + self.height - avatar_d - dp(8)

        initial_lbl = Label(
            text=letter,
            font_size=sp(20),
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(avatar_d, avatar_d),
            pos=(avatar_x, avatar_y),
            halign='center',
            valign='middle',
        )
        initial_lbl.bind(size=initial_lbl.setter('text_size'))
        self.add_widget(initial_lbl)

        # Username label below avatar
        display_name = self.username
        if len(display_name) > 9:
            display_name = display_name[:9] + '\u2026'

        name_lbl = Label(
            text=display_name,
            font_size=sp(11),
            color=theme.rgba_hex('#cbd5e1', 1.0),
            size_hint=(None, None),
            size=(self.width, dp(16)),
            pos=(self.x, self.y + dp(4)),
            halign='center',
            valign='middle',
        )
        name_lbl.bind(size=name_lbl.setter('text_size'))
        self.add_widget(name_lbl)

    def on_press(self):
        self._pressed = True
        self._update_canvas()

    def on_release(self):
        self._pressed = False
        self._update_canvas()
        if self._on_select:
            self._on_select(self.username)


class LoginScreen(FloatLayout):
    """Login screen with previous user tiles and username input."""

    def __init__(self, app_state, on_login=None, **kwargs):
        super().__init__(**kwargs)
        self._app_state = app_state
        self._on_login = on_login
        self._error = None

        # Background
        with self.canvas.before:
            Color(*theme.BG_DARK)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        # Check for existing users
        saved_users = app_state.get_sorted_users()
        has_users = len(saved_users) > 0

        # Calculate card height based on whether we have users
        card_height = 540 if has_users else 420

        # Center card container
        card = GradientCard(
            padding=[30, 30],
            size_hint=(None, None),
            size=(400, card_height),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
        )

        # Title
        title = Label(
            text='NEURO-MENTOR',
            font_size=32,
            bold=True,
            color=theme.GOLD,
            size_hint_y=None,
            height=50,
        )
        card.add_widget(title)

        # Subtitle
        subtitle = Label(
            text='Multi-User Brain Computer Interface System',
            font_size=theme.FONT_BODY_SMALL,
            color=theme.TEXT_MUTED,
            italic=True,
            size_hint_y=None,
            height=25,
        )
        card.add_widget(subtitle)

        # Spacer
        card.add_widget(Label(size_hint_y=None, height=12))

        # ============================================================
        # PREVIOUS USERS SECTION
        # ============================================================
        if has_users:
            # Section label
            prev_label = Label(
                text='PREVIOUS USERS',
                font_size=theme.FONT_HEADING_LARGE,
                bold=True,
                color=theme.TEXT_PRIMARY,
                size_hint_y=None,
                height=28,
                halign='left',
                valign='middle',
            )
            prev_label.bind(size=prev_label.setter('text_size'))
            card.add_widget(prev_label)

            # Spacer
            card.add_widget(Label(size_hint_y=None, height=8))

            # Horizontal scroll of user tiles
            tile_scroll = ScrollView(
                size_hint_y=None,
                height=dp(95),
                do_scroll_x=True,
                do_scroll_y=False,
            )
            tile_row = BoxLayout(
                orientation='horizontal',
                spacing=12,
                size_hint_x=None,
            )
            tile_row.bind(minimum_width=tile_row.setter('width'))

            for user in saved_users:
                tile = UserTile(
                    username=user.username,
                    on_select=self._quick_login,
                )
                tile_row.add_widget(tile)

            tile_scroll.add_widget(tile_row)
            card.add_widget(tile_scroll)

            # Spacer
            card.add_widget(Label(size_hint_y=None, height=8))

            # Divider line
            divider = Widget(size_hint_y=None, height=dp(1))
            with divider.canvas:
                Color(*theme.rgba_hex('#334155', 1.0))
                divider._line = Rectangle(pos=divider.pos, size=divider.size)
            divider.bind(
                pos=lambda inst, val: setattr(inst._line, 'pos', val),
                size=lambda inst, val: setattr(inst._line, 'size', val),
            )
            card.add_widget(divider)

            # "OR SIGN IN AS NEW USER" label
            or_label = Label(
                text='OR SIGN IN AS NEW USER',
                font_size=sp(11),
                color=theme.rgba_hex('#64748b', 1.0),
                size_hint_y=None,
                height=24,
                halign='center',
                valign='middle',
            )
            or_label.bind(size=or_label.setter('text_size'))
            card.add_widget(or_label)
        else:
            # Info text when no previous users
            info = Label(
                text='Enter your username to login or create a new profile.\n'
                     'Each user has isolated data and trained models.',
                font_size=theme.FONT_BODY_SMALL,
                color=theme.TEXT_SECONDARY,
                halign='center',
                valign='middle',
                size_hint_y=None,
                height=50,
            )
            info.bind(size=info.setter('text_size'))
            card.add_widget(info)

        # ============================================================
        # NEW USER INPUT SECTION
        # ============================================================

        # Username label
        usr_label = Label(
            text='USERNAME',
            font_size=theme.FONT_BODY_SMALL,
            color=theme.GOLD,
            bold=True,
            size_hint_y=None,
            height=20,
            halign='left',
            valign='middle',
        )
        usr_label.bind(size=usr_label.setter('text_size'))
        card.add_widget(usr_label)

        # Username input
        self._username_input = TextInput(
            hint_text='Enter your username (alphanumeric)',
            font_size=theme.FONT_BODY_REGULAR,
            multiline=False,
            size_hint_y=None,
            height=40,
            background_color=theme.INPUT_BG,
            foreground_color=theme.TEXT_PRIMARY,
            hint_text_color=theme.TEXT_MUTED,
            cursor_color=theme.TEAL,
            padding=[12, 10],
        )
        self._username_input.bind(on_text_validate=lambda *a: self._login())
        card.add_widget(self._username_input)

        # Help text
        help_lbl = Label(
            text='Use letters, numbers, and underscores only',
            font_size=theme.FONT_BODY_SMALL,
            color=theme.TEXT_MUTED,
            size_hint_y=None,
            height=20,
            halign='left',
            valign='middle',
        )
        help_lbl.bind(size=help_lbl.setter('text_size'))
        card.add_widget(help_lbl)

        # Error label
        self._error_lbl = Label(
            text='',
            font_size=theme.FONT_BODY_SMALL,
            color=theme.RED,
            size_hint_y=None,
            height=20,
            halign='left',
            valign='middle',
        )
        self._error_lbl.bind(size=self._error_lbl.setter('text_size'))
        card.add_widget(self._error_lbl)

        # Login button
        login_btn = ShadowButton(
            text='ENTER SYSTEM',
            font_size=theme.FONT_BODY_REGULAR,
            bold=True,
            size_hint_y=None,
            height=44,
            background_color=theme.GOLD,
            color=(0, 0, 0, 1),
        )
        login_btn.bind(on_press=lambda *a: self._login())
        card.add_widget(login_btn)

        self.add_widget(card)

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def _quick_login(self, username):
        """Login via user tile tap."""
        self._app_state.login(username)
        if self._on_login:
            self._on_login()

    def _login(self):
        username = self._username_input.text.strip()

        if not username:
            self._error_lbl.text = 'Username cannot be empty'
            return

        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            self._error_lbl.text = 'Username: letters, numbers, underscores only'
            return

        self._error_lbl.text = ''
        self._app_state.login(username)
        if self._on_login:
            self._on_login()
