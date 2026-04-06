"""
NeuroMentor Application State
Observable state management using Kivy EventDispatcher (replaces Flutter Provider).
"""
from kivy.event import EventDispatcher
from kivy.properties import (
    ObjectProperty, NumericProperty, StringProperty
)
from datetime import datetime
import json
import os

class UserProfile:
    """User profile data."""
    def __init__(self, username, name='', age='', notes='', created_date=None, scores=None, last_login=None):
        self.username = username
        self.name = name or username
        self.age = age
        self.notes = notes
        self.created_date = created_date or datetime.now().isoformat()
        self.scores = scores or []
        self.last_login = last_login or datetime.now().isoformat()

    def to_dict(self):
        return {
            'username': self.username,
            'name': self.name,
            'age': self.age,
            'notes': self.notes,
            'created_date': self.created_date,
            'scores': self.scores,
            'last_login': self.last_login,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            username=data.get('username', ''),
            name=data.get('name', ''),
            age=data.get('age', ''),
            notes=data.get('notes', ''),
            created_date=data.get('created_date'),
            scores=data.get('scores', []),
            last_login=data.get('last_login'),
        )


class AppState(EventDispatcher):
    """
    Main application state.
    Uses Kivy properties for automatic UI binding.
    """
    current_user = ObjectProperty(None, allownone=True)
    selected_page_index = NumericProperty(0)
    selected_port = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.users_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'users.json')
        self.all_users = self._load_users()

    def _load_users(self):
        if not os.path.exists(self.users_file):
            return {}
        try:
            with open(self.users_file, 'r') as f:
                data = json.load(f)
                return {k: UserProfile.from_dict(v) for k, v in data.items()}
        except Exception as e:
            print(f"Error loading users: {e}")
            return {}

    def _save_users(self):
        try:
            with open(self.users_file, 'w') as f:
                json.dump({k: v.to_dict() for k, v in self.all_users.items()}, f, indent=4)
        except Exception as e:
            print(f"Error saving users: {e}")

    def save_current_user_score(self, test_name, score):
        if self.current_user:
            self.current_user.scores.append({'test': test_name, 'score': score, 'date': datetime.now().isoformat()})
            self._save_users()

    def get_sorted_users(self):
        """Return list of UserProfile sorted by last_login descending (most recent first)."""
        users = list(self.all_users.values())
        users.sort(key=lambda u: u.last_login or '', reverse=True)
        return users

    # ============================================================
    # USER MANAGEMENT
    # ============================================================

    def login(self, username):
        """Login with username - creates profile if not exists."""
        if username not in self.all_users:
            self.all_users[username] = UserProfile(username=username, name=username)
        self.all_users[username].last_login = datetime.now().isoformat()
        self._save_users()
        self.current_user = self.all_users[username]
        self.selected_page_index = 0

        # Attempt to load RF model for this user
        self._load_rf_model(username)

    def logout(self):
        """Logout current user."""
        self._save_users()
        self.current_user = None
        self.selected_page_index = 0

    def update_profile(self, name=None, age=None, notes=None):
        """Update user profile fields."""
        if self.current_user is not None:
            if name is not None:
                self.current_user.name = name
            if age is not None:
                self.current_user.age = age
            if notes is not None:
                self.current_user.notes = notes
            self._save_users()
            # Force property change notification
            self.property('current_user').dispatch(self)

    # ============================================================
    # NAVIGATION
    # ============================================================

    def set_selected_page(self, index):
        """Set the currently selected page index."""
        self.selected_page_index = index

    def set_selected_port(self, port):
        """Set the selected device port."""
        self.selected_port = port or ''

    # ============================================================
    # RF MODEL PERSISTENCE
    # ============================================================

    def _get_rf_model_dir(self, username):
        """Get the directory path for a user's RF model."""
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'neuromentor_data')
        user_model_dir = os.path.join(data_dir, f'{username}_rf_model')
        os.makedirs(user_model_dir, exist_ok=True)
        return user_model_dir

    def _get_bundled_model_dir(self):
        """Get the path to the bundled pre-trained RF model."""
        # The bundled model lives at: Kivy_Section/rf_model/rf_model/
        project_root = os.path.dirname(os.path.abspath(__file__))
        bundled = os.path.join(project_root, '..', 'rf_model', 'rf_model')
        return os.path.normpath(bundled)

    def save_rf_model(self, rf_classifier=None):
        """Save the RF model for the current user."""
        if rf_classifier is None:
            rf_classifier = getattr(self, 'rf_classifier', None)
        if self.current_user and rf_classifier and rf_classifier.is_trained:
            dirpath = self._get_rf_model_dir(self.current_user.username)
            rf_classifier.save(dirpath)
            print(f"[AppState] RF model saved to {dirpath}")

    def _load_rf_model(self, username):
        """Attempt to load an RF model for the given user.

        Tries user-specific model first, then falls back to bundled model.
        Returns True if loaded.
        """
        from services.rf_classifier import RFClassifier

        if not hasattr(self, 'rf_classifier'):
            self.rf_classifier = RFClassifier()

        # 1. Try user-specific model
        user_dir = self._get_rf_model_dir(username)
        model_file = os.path.join(user_dir, 'rf_eeg_model.pkl')
        if os.path.exists(model_file):
            try:
                success = self.rf_classifier.load(user_dir)
                if success:
                    print(f"[AppState] User RF model loaded for {username}")
                    return True
            except Exception as e:
                print(f"[AppState] Could not load user RF model: {e}")

        # 2. Fall back to bundled pre-trained model
        bundled_dir = self._get_bundled_model_dir()
        bundled_model = os.path.join(bundled_dir, 'rf_eeg_model.pkl')
        if os.path.exists(bundled_model):
            try:
                success = self.rf_classifier.load(bundled_dir)
                if success:
                    print(f"[AppState] Bundled RF model loaded for {username}")
                    return True
            except Exception as e:
                print(f"[AppState] Could not load bundled RF model: {e}")

        print(f"[AppState] No RF model available for {username}")
        return False
