"""
NeuroMentor - EEG Brain-Computer Interface Application
Kivy version for Android APK generation via Buildozer.

Entry point: run this file to start the application.
"""
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.config import Config
# Disable multi-touch emulation (red dots) on desktop
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
# Lock orientation to portrait on desktop
Config.set('graphics', 'rotation', '0')

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout

# Portrait mobile phone aspect ratio (like iPhone 14: 390x844)
Window.size = (390, 844)

import theme
from app_state import AppState
from screens.login_screen import LoginScreen
from screens.main_shell import MainShell


class NeuroMentorApp(App):
    """Main NeuroMentor Kivy Application."""

    def build(self):
        # Lock orientation to portrait on Android via jnius
        try:
            from jnius import autoclass
            activity = autoclass('org.kivy.android.PythonActivity').mActivity
            activity.setRequestedOrientation(1)  # 1 = SCREEN_ORIENTATION_PORTRAIT
        except ImportError:
            pass  # Not on Android, skip

        self.title = 'NeuroMentor'

        # Set dark background
        Window.clearcolor = theme.BG_DARK

        # Create app state
        self.app_state = AppState()

        # Root container
        self.root_container = FloatLayout()

        # Show login screen initially
        self._show_login()

        # Listen for user changes
        self.app_state.bind(current_user=self._on_user_change)

        return self.root_container

    def _on_user_change(self, *args):
        """Handle user login/logout."""
        if self.app_state.current_user is None:
            self._show_login()
        else:
            self._show_main()

    def _show_login(self):
        """Show the login screen."""
        self.root_container.clear_widgets()
        login = LoginScreen(
            app_state=self.app_state,
            on_login=self._show_main,
        )
        self.root_container.add_widget(login)

    def _show_main(self, *args):
        """Show the main app shell."""
        self.root_container.clear_widgets()
        main_shell = MainShell(
            app_state=self.app_state,
            on_logout=self._show_login,
        )
        self.root_container.add_widget(main_shell)


if __name__ == '__main__':
    NeuroMentorApp().run()
