"""
Profile screen matching Flutter's ProfileScreen.
Form with name, age, notes fields and save button.
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from widgets.custom_ui import ShadowButton
from kivy.uix.popup import Popup
from widgets.custom_ui import ShadowButton, GradientCard
from kivy.graphics import Color, RoundedRectangle, Rectangle
import theme


class ProfileScreen(BoxLayout):
    """User profile editing form."""

    def __init__(self, app_state, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=15, **kwargs)
        self._app_state = app_state

        # Title banner
        title_box = GradientCard(
            size_hint_y=None, height=50, padding=[10, 10], radius=10
        )
        title_lbl = Label(
            text='USER PROFILE',
            font_size=theme.FONT_TITLE_MEDIUM,
            bold=True,
            color=theme.GOLD,
            halign='left',
            valign='middle',
        )
        title_lbl.bind(size=title_lbl.setter('text_size'))
        title_box.add_widget(title_lbl)
        self.add_widget(title_box)

        # Form container
        form_box = GradientCard(
            padding=[20, 20]
        )
        # Full Name
        name_lbl = Label(
            text='FULL NAME:',
            font_size=theme.FONT_BODY_REGULAR,
            color=theme.TEAL,
            bold=True,
            size_hint_y=None,
            height=20,
            halign='left',
            valign='middle',
        )
        name_lbl.bind(size=name_lbl.setter('text_size'))
        form_box.add_widget(name_lbl)

        self._name_input = TextInput(
            font_size=theme.FONT_BODY_REGULAR,
            multiline=False,
            size_hint_y=None,
            height=40,
            background_color=theme.INPUT_BG,
            foreground_color=theme.TEXT_PRIMARY,
            cursor_color=theme.TEAL,
            padding=[12, 10],
        )
        form_box.add_widget(self._name_input)

        # Age
        age_lbl = Label(
            text='AGE:',
            font_size=theme.FONT_BODY_REGULAR,
            color=theme.TEAL,
            bold=True,
            size_hint_y=None,
            height=20,
            halign='left',
            valign='middle',
        )
        age_lbl.bind(size=age_lbl.setter('text_size'))
        form_box.add_widget(age_lbl)

        self._age_input = TextInput(
            font_size=theme.FONT_BODY_REGULAR,
            multiline=False,
            input_filter='int',
            size_hint_y=None,
            height=40,
            background_color=theme.INPUT_BG,
            foreground_color=theme.TEXT_PRIMARY,
            cursor_color=theme.TEAL,
            padding=[12, 10],
        )
        form_box.add_widget(self._age_input)

        # Clinical Notes
        notes_lbl = Label(
            text='CLINICAL NOTES:',
            font_size=theme.FONT_BODY_REGULAR,
            color=theme.TEAL,
            bold=True,
            size_hint_y=None,
            height=20,
            halign='left',
            valign='middle',
        )
        notes_lbl.bind(size=notes_lbl.setter('text_size'))
        form_box.add_widget(notes_lbl)

        self._notes_input = TextInput(
            font_size=theme.FONT_BODY_REGULAR,
            multiline=True,
            size_hint_y=None,
            height=120,
            background_color=theme.INPUT_BG,
            foreground_color=theme.TEXT_PRIMARY,
            cursor_color=theme.TEAL,
            padding=[12, 10],
        )
        form_box.add_widget(self._notes_input)

        self.add_widget(form_box)

        # Save button
        save_btn = ShadowButton(
            text='SAVE PROFILE DATA',
            font_size=theme.FONT_BODY_REGULAR,
            bold=True,
            size_hint_y=None,
            height=45,
            background_color=theme.GOLD,
            color=(0, 0, 0, 1),
        )
        save_btn.bind(on_press=lambda *a: self._save_profile())
        self.add_widget(save_btn)

        # Load initial profile data
        app_state.bind(current_user=self._load_profile)
        self._load_profile()

    def _load_profile(self, *args):
        user = self._app_state.current_user
        if user:
            self._name_input.text = user.name or ''
            self._age_input.text = user.age or ''
            self._notes_input.text = user.notes or ''

    def _save_profile(self):
        self._app_state.update_profile(
            name=self._name_input.text,
            age=self._age_input.text,
            notes=self._notes_input.text,
        )
        # Show feedback popup
        popup = Popup(
            title='',
            content=Label(
                text='PROFILE UPDATED.',
                font_size=theme.FONT_BODY_REGULAR,
                color=theme.TEXT_PRIMARY,
            ),
            size_hint=(None, None),
            size=(250, 120),
            background_color=theme.PANEL_BG,
            auto_dismiss=True,
        )
        popup.open()
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: popup.dismiss(), 1.5)
