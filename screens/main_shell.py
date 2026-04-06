"""
Main shell with collapsible sidebar navigation.
Matches Flutter's MainShell with animated sidebar overlay.
"""
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from widgets.custom_ui import ShadowButton, MenuBurgerButton
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.animation import Animation
from kivy.properties import BooleanProperty, NumericProperty
from kivy.clock import Clock
import theme


PAGE_NAMES = ['DASHBOARD', 'PROFILE', 'CALIBRATE', 'RANDOM FOREST', 'LIVE FEED']
SIDEBAR_WIDTH = 240


class MainShell(FloatLayout):
    """Main app shell with top bar, sidebar overlay, and screen switching."""

    sidebar_open = BooleanProperty(False)

    def __init__(self, app_state, on_logout=None, **kwargs):
        super().__init__(**kwargs)
        self._app_state = app_state
        self._on_logout = on_logout
        self._screens = {}
        self._current_screen = None

        # Background
        with self.canvas.before:
            Color(*theme.BG_DARK)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        # ============================================================
        # MAIN CONTENT (top bar + screen area) - full width always
        # ============================================================
        self._main_column = BoxLayout(orientation='vertical')

        # Top bar
        top_bar = BoxLayout(
            size_hint_y=None, height=50,
            padding=[8, 0], spacing=10,
        )
        with top_bar.canvas.before:
            Color(*theme.SIDEBAR_BG)
            top_bar._bg = Rectangle(pos=top_bar.pos, size=top_bar.size)
            Color(*theme.SIDEBAR_BORDER)
            top_bar._border = Rectangle(pos=top_bar.pos, size=(1, 1))
        def _update_top_bar(inst, val):
            inst._bg.pos = inst.pos
            inst._bg.size = inst.size
            inst._border.pos = (inst.x, inst.y)
            inst._border.size = (inst.width, 1)
        top_bar.bind(pos=_update_top_bar, size=_update_top_bar)

        # Menu toggle button
        self._menu_btn = MenuBurgerButton(
            size_hint=(None, None),
            size=(45, 40),
            pos_hint={'center_y': 0.5},
            color=theme.GOLD,
        )
        self._menu_btn.bind(on_press=lambda *a: self._toggle_sidebar())
        top_bar.add_widget(self._menu_btn)

        # App title
        title = Label(
            text='NEUROMENTOR',
            font_size=theme.FONT_HEADING_MEDIUM,
            bold=True,
            color=theme.GOLD,
            size_hint_x=None,
            width=160,
            halign='left',
            valign='middle',
        )
        title.bind(size=title.setter('text_size'))
        top_bar.add_widget(title)

        # Spacer
        top_bar.add_widget(Label())

        # Page indicator
        self._page_indicator = Label(
            text='DASHBOARD',
            font_size=theme.FONT_BODY_SMALL,
            color=theme.TEXT_MUTED,
            size_hint_x=None,
            width=100,
            halign='right',
            valign='middle',
        )
        self._page_indicator.bind(size=self._page_indicator.setter('text_size'))
        top_bar.add_widget(self._page_indicator)

        self._main_column.add_widget(top_bar)

        # Screen content area
        self._screen_area = BoxLayout()
        self._main_column.add_widget(self._screen_area)

        self.add_widget(self._main_column)

        # ============================================================
        # BACKDROP (semi-transparent overlay, dismisses sidebar on tap)
        # ============================================================
        self._backdrop = _Backdrop(on_tap=self._close_sidebar)
        self._backdrop.opacity = 0
        self.add_widget(self._backdrop)

        # ============================================================
        # SIDEBAR (slides in from left over content)
        # ============================================================
        self._sidebar = SidebarNavigation(
            app_state=app_state,
            on_item_selected=self._close_sidebar,
            on_switch_user=self._handle_switch_user,
            size_hint=(None, 1),
            width=SIDEBAR_WIDTH,
        )
        self._sidebar.x = -SIDEBAR_WIDTH  # Start off-screen
        self.add_widget(self._sidebar)

        # Build screens
        self._build_screens()

        # Listen for page changes
        app_state.bind(selected_page_index=self._on_page_change)
        self._on_page_change()

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def _build_screens(self):
        from screens.dashboard_screen import DashboardScreen
        from screens.profile_screen import ProfileScreen
        from screens.calibration_screen import CalibrationScreen
        from screens.random_forest_screen import RandomForestScreen
        from screens.monitoring_screen import MonitoringScreen

        self._screens = {
            0: DashboardScreen(app_state=self._app_state),
            1: ProfileScreen(app_state=self._app_state),
            2: CalibrationScreen(app_state=self._app_state),
            3: RandomForestScreen(app_state=self._app_state),
            4: MonitoringScreen(app_state=self._app_state),
        }

    def _on_page_change(self, *args):
        idx = self._app_state.selected_page_index
        self._page_indicator.text = PAGE_NAMES[idx] if idx < len(PAGE_NAMES) else ''

        self._screen_area.clear_widgets()
        screen = self._screens.get(idx)
        if screen:
            self._screen_area.add_widget(screen)
            self._current_screen = screen

    def _toggle_sidebar(self):
        if self.sidebar_open:
            self._close_sidebar()
        else:
            self._open_sidebar()

    def _open_sidebar(self):
        if self.sidebar_open:
            return
        self.sidebar_open = True

        # Show backdrop with fade-in
        anim_backdrop = Animation(opacity=1, duration=0.25, t='out_quad')
        anim_backdrop.start(self._backdrop)
        self._backdrop.active = True

        # Slide sidebar in
        anim_sidebar = Animation(x=self.x, duration=0.25, t='out_quad')
        anim_sidebar.start(self._sidebar)

        # Change menu icon to X
        self._menu_btn.set_open(True)

    def _close_sidebar(self, *args):
        if not self.sidebar_open:
            return
        self.sidebar_open = False

        # Fade out backdrop
        anim_backdrop = Animation(opacity=0, duration=0.25, t='out_quad')
        anim_backdrop.start(self._backdrop)
        self._backdrop.active = False

        # Slide sidebar out
        anim_sidebar = Animation(x=self.x - SIDEBAR_WIDTH, duration=0.25, t='out_quad')
        anim_sidebar.start(self._sidebar)

        # Change menu icon back to hamburger
        self._menu_btn.set_open(False)

    def _handle_switch_user(self):
        self._close_sidebar()
        self._app_state.logout()
        if self._on_logout:
            self._on_logout()


class _Backdrop(Widget):
    """Semi-transparent overlay that dismisses sidebar on tap."""

    active = BooleanProperty(False)

    def __init__(self, on_tap=None, **kwargs):
        super().__init__(**kwargs)
        self._on_tap = on_tap

        with self.canvas:
            Color(0, 0, 0, 0.5)
            self._rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(
            pos=lambda inst, val: setattr(inst._rect, 'pos', val),
            size=lambda inst, val: setattr(inst._rect, 'size', val),
        )

    def on_touch_down(self, touch):
        if self.active and self.collide_point(*touch.pos):
            if self._on_tap:
                self._on_tap()
            return True
        return False


class SidebarNavigation(BoxLayout):
    """Sidebar navigation panel with nav buttons, signal indicator, switch user."""

    def __init__(self, app_state, on_item_selected=None,
                 on_switch_user=None, **kwargs):
        super().__init__(orientation='vertical', padding=[0, 15], **kwargs)
        self._app_state = app_state
        self._on_item_selected = on_item_selected
        self._on_switch_user = on_switch_user
        self._nav_buttons = []

        # Background
        with self.canvas.before:
            Color(*theme.SIDEBAR_BG)
            self._bg = Rectangle(pos=self.pos, size=self.size)
            Color(*theme.SIDEBAR_BORDER)
            self._right_border = Rectangle(pos=self.pos, size=(1, 1))

        def _update_sidebar_bg(inst, val):
            inst._bg.pos = inst.pos
            inst._bg.size = inst.size
            inst._right_border.pos = (inst.x + inst.width - 1, inst.y)
            inst._right_border.size = (1, inst.height)
        self.bind(pos=_update_sidebar_bg, size=_update_sidebar_bg)

        # Logo / Title
        logo = Label(
            text='NEURO\nMENTOR',
            font_size=theme.FONT_TITLE_LARGE,
            bold=True,
            color=theme.GOLD,
            size_hint_y=None,
            height=80,
            halign='center',
        )
        self.add_widget(logo)

        # Spacer
        self.add_widget(Label(size_hint_y=None, height=20))

        # Navigation buttons
        for idx, name in enumerate(PAGE_NAMES):
            btn = NavShadowButton(
                text=name,
                nav_index=idx,
                app_state=app_state,
                on_selected=self._on_nav_select,
            )
            self._nav_buttons.append(btn)
            self.add_widget(btn)

        # Spacer (takes remaining space)
        self.add_widget(Label())

        # Signal indicator
        signal_row = BoxLayout(
            size_hint_y=None, height=25, padding=[15, 0], spacing=8,
        )
        sig_label = Label(
            text='SIGNAL:',
            font_size=theme.FONT_BODY_SMALL,
            color=theme.TEXT_MUTED,
            size_hint_x=None,
            width=60,
            halign='left',
            valign='middle',
        )
        sig_label.bind(size=sig_label.setter('text_size'))
        signal_row.add_widget(sig_label)

        # LED circle
        led = Label(
            text='\u25cf',
            font_size=16,
            color=(0.2, 0.2, 0.2, 1),
            size_hint_x=None,
            width=20,
        )
        signal_row.add_widget(led)

        idle_label = Label(
            text='IDLE',
            font_size=theme.FONT_BODY_SMALL,
            color=theme.TEXT_MUTED,
            halign='left',
            valign='middle',
        )
        idle_label.bind(size=idle_label.setter('text_size'))
        signal_row.add_widget(idle_label)
        self.add_widget(signal_row)

        # Spacer
        self.add_widget(Label(size_hint_y=None, height=10))

        # Switch user button
        switch_btn = ShadowButton(
            text='\U0001f504 SWITCH USER',
            font_size=theme.FONT_BODY_REGULAR,
            size_hint_y=None,
            height=40,
            background_color=(0.133, 0.133, 0.133, 1),
            color=theme.TEAL,
        )
        switch_btn.bind(on_press=lambda *a: self._show_switch_dialog())
        switch_row = BoxLayout(size_hint_y=None, height=55, padding=[15, 8])
        switch_row.add_widget(switch_btn)
        self.add_widget(switch_row)

    def _on_nav_select(self, index):
        self._app_state.set_selected_page(index)
        if self._on_item_selected:
            self._on_item_selected()

    def _show_switch_dialog(self):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        msg = Label(
            text='This will end the current session\nand return to login. Continue?',
            font_size=theme.FONT_BODY_REGULAR,
            color=theme.TEXT_SECONDARY,
            halign='center',
        )
        msg.bind(size=msg.setter('text_size'))
        content.add_widget(msg)

        btn_row = BoxLayout(size_hint_y=None, height=40, spacing=10)
        no_btn = ShadowButton(
            text='No',
            font_size=theme.FONT_BODY_REGULAR,
            background_color=theme.PANEL_BG,
            color=theme.TEXT_MUTED,
        )
        yes_btn = ShadowButton(
            text='Yes',
            font_size=theme.FONT_BODY_REGULAR,
            background_color=theme.PANEL_BG,
            color=theme.GOLD,
        )
        btn_row.add_widget(no_btn)
        btn_row.add_widget(yes_btn)
        content.add_widget(btn_row)

        popup = Popup(
            title='SWITCH USER',
            title_color=theme.TEXT_PRIMARY,
            content=content,
            size_hint=(None, None),
            size=(320, 200),
            background_color=theme.PANEL_BG,
            auto_dismiss=True,
        )

        no_btn.bind(on_press=lambda *a: popup.dismiss())

        def _yes_pressed(*a):
            popup.dismiss()
            if self._on_switch_user:
                self._on_switch_user()
        yes_btn.bind(on_press=_yes_pressed)
        popup.open()


class NavShadowButton(BoxLayout):
    """
    Navigation button with selection highlight matching Flutter's style:
    - Gold left border accent when selected
    - Gold text when selected, muted text otherwise
    - Subtle background tint when selected
    """

    def __init__(self, text, nav_index, app_state, on_selected=None, **kwargs):
        super().__init__(
            size_hint_y=None, height=48,
            padding=[0, 2],
            **kwargs,
        )
        self._nav_index = nav_index
        self._app_state = app_state
        self._on_selected = on_selected
        self._text = text

        # Selection accent (left border, 4px wide)
        with self.canvas.before:
            self._sel_bg_color = Color(
                theme.GOLD[0], theme.GOLD[1], theme.GOLD[2], 0
            )
            self._sel_bg = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[8]
            )
            self._accent_color = Color(*theme.GOLD, 0)
            self._accent_rect = Rectangle(
                pos=self.pos, size=(4, 1)
            )

        self._btn = ShadowButton(
            text=text,
            font_size=theme.FONT_BODY_REGULAR,
            halign='left',
            valign='middle',
            background_color=theme.TRANSPARENT,
            color=theme.TEXT_MUTED,
            padding=[14, 0],
        )
        self._btn.bind(on_press=lambda *a: self._select())
        self._btn.bind(size=self._btn.setter('text_size'))
        self.add_widget(self._btn)

        # Update styling when selection changes
        app_state.bind(selected_page_index=self._update_style)
        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self._update_style()

    def _select(self):
        if self._on_selected:
            self._on_selected(self._nav_index)

    def _update_canvas(self, *args):
        self._sel_bg.pos = (self.x + 8, self.y + 2)
        self._sel_bg.size = (self.width - 16, self.height - 4)
        self._accent_rect.pos = (self.x + 8, self.y + 2)
        self._accent_rect.size = (4, self.height - 4)

    def _update_style(self, *args):
        is_selected = (self._app_state.selected_page_index == self._nav_index)
        if is_selected:
            self._btn.color = theme.GOLD
            self._btn.bold = True
            self._sel_bg_color.rgba = (
                theme.GOLD[0], theme.GOLD[1], theme.GOLD[2], 0.1
            )
            self._accent_color.a = 1
        else:
            self._btn.color = theme.TEXT_MUTED
            self._btn.bold = False
            self._sel_bg_color.a = 0
            self._accent_color.a = 0
        self._update_canvas()
