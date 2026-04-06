"""
Random Forest training screen.
Simulated Random Forest training pipeline with console output.
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from widgets.custom_ui import ShadowButton, GradientCard
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.clock import Clock
import theme


class RandomForestScreen(BoxLayout):
    """Random Forest training UI with console output."""

    def __init__(self, app_state, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=15, **kwargs)
        self._app_state = app_state
        self._log_lines = []
        self._is_training = False
        self._is_checking = False
        self._scheduled_events = []

        # Title
        title = Label(
            text='RANDOM FOREST TRAINING',
            font_size=theme.FONT_TITLE_MEDIUM,
            bold=True,
            color=theme.GOLD,
            size_hint_y=None,
            height=35,
            halign='left',
            valign='middle',
        )
        title.bind(size=title.setter('text_size'))
        self.add_widget(title)

        # Console output
        console_box = GradientCard(padding=[10, 10])

        scroll = ScrollView()
        self._console_label = Label(
            text='',
            font_size=theme.FONT_BODY_REGULAR,
            color=theme.TEAL,
            halign='left',
            valign='top',
            size_hint_y=None,
            markup=False,
            padding=[10, 10],
        )
        self._console_label.bind(
            texture_size=lambda inst, sz: setattr(inst, 'height', max(sz[1], 100)),
            width=lambda inst, w: setattr(inst, 'text_size', (w - 20, None)),
        )
        scroll.add_widget(self._console_label)
        console_box.add_widget(scroll)
        self.add_widget(console_box)

        # Generate demo data button
        self._demo_btn = ShadowButton(
            text='GENERATE DEMO DATA (TESTING)',
            font_size=theme.FONT_BODY_REGULAR,
            bold=True,
            size_hint_y=None,
            height=44,
            background_color=theme.BUTTON_BG,
            color=theme.GOLD,
        )
        self._demo_btn.bind(on_press=lambda *a: self._generate_demo_data())
        self.add_widget(self._demo_btn)

        # Train button
        self._train_btn = ShadowButton(
            text='EXECUTE TRAINING PIPELINE',
            font_size=theme.FONT_BODY_REGULAR,
            bold=True,
            size_hint_y=None,
            height=44,
            background_color=theme.BUTTON_BG,
            color=theme.GOLD,
        )
        self._train_btn.bind(on_press=lambda *a: self._start_training())
        self.add_widget(self._train_btn)

        # ── Compatibility check button ──
        self._compat_btn = ShadowButton(
            text='RUN COMPATIBILITY CHECK',
            font_size=theme.FONT_BODY_REGULAR,
            bold=True,
            size_hint_y=None,
            height=44,
            background_color=theme.BUTTON_BG,
            color=theme.GOLD,
        )
        self._compat_btn.bind(on_press=lambda *a: self._run_compat_check())
        self.add_widget(self._compat_btn)

        # ── Compatibility check output area ──
        compat_title = Label(
            text='COMPATIBILITY DIAGNOSTIC',
            font_size=theme.FONT_BODY_REGULAR,
            bold=True,
            color=theme.TEXT_SECONDARY,
            size_hint_y=None,
            height=25,
            halign='left',
            valign='middle',
        )
        compat_title.bind(size=compat_title.setter('text_size'))
        self.add_widget(compat_title)

        compat_card = GradientCard(padding=[10, 10])
        compat_scroll = ScrollView()
        self._compat_label = Label(
            text='Press RUN COMPATIBILITY CHECK to diagnose pipeline.',
            font_size=theme.FONT_BODY_SMALL,
            color=theme.TEAL,
            halign='left',
            valign='top',
            size_hint_y=None,
            markup=False,
            padding=[10, 10],
        )
        self._compat_label.bind(
            texture_size=lambda inst, sz: setattr(inst, 'height', max(sz[1], 80)),
            width=lambda inst, w: setattr(inst, 'text_size', (w - 20, None)),
        )
        compat_scroll.add_widget(self._compat_label)
        compat_card.add_widget(compat_scroll)
        self.add_widget(compat_card)

    def _add_log(self, line):
        self._log_lines.append(line)
        self._console_label.text = '\n'.join(self._log_lines)

    def _clear_log(self):
        self._log_lines.clear()
        self._console_label.text = ''

    def _generate_demo_data(self):
        if self._is_training:
            return
        self._clear_log()
        self._add_log('>>> GENERATING SYNTHETIC EEG DATASET...')
        self._add_log('>>> Simulating 12-feature band power vectors...')
        ev = Clock.schedule_once(lambda dt: self._finish_demo(), 1.0)
        self._scheduled_events.append(ev)

    def _finish_demo(self):
        self._add_log('>>> SUCCESS. Generated 1440 samples (480 per class).')
        self._add_log('>>> Features: delta, theta, alpha, beta, gamma power,')
        self._add_log('    focus_index, stress_index, alpha_theta_ratio,')
        self._add_log('    beta_alpha_ratio, delta_alpha_ratio,')
        self._add_log('    spectral_entropy, mean_power')
        self._add_log('>>> You can now EXECUTE TRAINING PIPELINE.')

    def _start_training(self):
        if self._is_training:
            return
        self._is_training = True
        self._train_btn.text = 'TRAINING...'
        self._train_btn.disabled = True
        self._demo_btn.disabled = True
        self._compat_btn.disabled = True

        self._clear_log()
        self._add_log('>>> INITIATING RANDOM FOREST TRAINING PIPELINE...')
        self._simulate_training()

    def _simulate_training(self):
        """Simulate the 9-step Random Forest training pipeline."""
        self._unschedule_all()

        steps = [
            # Step 1 (0.2s)
            (0.2, [
                '[INFO] Loading calibration session data...',
                '[INFO] Found 3 classes: Calm, Stressed, Focused',
            ]),
            # Step 2 (0.5s)
            (0.5, [
                '[INFO] Feature extraction complete.',
                '[INFO] Samples: Calm=480  Stressed=480  Focused=480',
                '[INFO] Feature vector size: 12 features per sample',
                '[INFO] Total dataset: 1440 samples',
            ]),
            # Step 3 (0.9s)
            (0.9, [
                '[INFO] Applying StandardScaler normalization...',
                '[INFO] Mean per feature: [0.82, 1.14, 2.31, ...]',
                '[INFO] Std  per feature: [0.21, 0.33, 0.58, ...]',
            ]),
            # Step 4 (1.3s)
            (1.3, [
                '[INFO] Splitting dataset: 80% train / 20% test',
                '[INFO] Train: 1152 samples | Test: 288 samples',
                '[INFO] Stratified split \u2014 class balance preserved',
            ]),
            # Step 5 (1.8s)
            (1.8, [
                '[INFO] Running 5-fold cross-validation...',
                '[INFO] Fold 1/5 \u2014 CV Accuracy: 87.3%',
                '[INFO] Fold 2/5 \u2014 CV Accuracy: 89.1%',
                '[INFO] Fold 3/5 \u2014 CV Accuracy: 86.8%',
                '[INFO] Fold 4/5 \u2014 CV Accuracy: 90.2%',
                '[INFO] Fold 5/5 \u2014 CV Accuracy: 88.6%',
                '[INFO] Mean CV Accuracy: 88.4% \u00b1 1.2%',
            ]),
            # Step 6 (2.5s)
            (2.5, [
                '[INFO] Training RandomForestClassifier...',
                '[INFO] n_estimators=200  max_depth=None',
                '[INFO] min_samples_split=2  n_jobs=-1',
                '[INFO] Building tree   1/200...',
                '[INFO] Building tree  50/200...',
                '[INFO] Building tree 100/200...',
                '[INFO] Building tree 150/200...',
                '[INFO] Building tree 200/200...',
            ]),
            # Step 7 (3.5s)
            (3.5, [
                '[INFO] Training complete.',
                '[INFO] OOB Score: 91.2%',
                '[INFO] Test Accuracy: 90.6%',
                '[INFO] ',
                '[INFO] Classification Report:',
                '[INFO]              precision  recall  f1-score',
                '[INFO] Calm           0.93      0.91    0.92',
                '[INFO] Stressed       0.89      0.90    0.89',
                '[INFO] Focused        0.92      0.93    0.92',
            ]),
            # Step 8 (4.2s)
            (4.2, [
                '[INFO] Feature Importances (top 5):',
                '[INFO] 1. focus_index        0.187',
                '[INFO] 2. alpha_power        0.163',
                '[INFO] 3. stress_index       0.141',
                '[INFO] 4. beta_power         0.128',
                '[INFO] 5. spectral_entropy   0.097',
            ]),
            # Step 9 (4.8s)
            (4.8, [
                '[INFO] Saving model to user profile...',
                '[INFO] Model size: 2.3 MB',
                '[SUCCESS] Random Forest model saved. \u2713',
                '[SUCCESS] User profile updated. \u2713',
                '[SUCCESS] Ready for live classification. \u2713',
            ]),
        ]

        for delay, lines in steps:
            ev = Clock.schedule_once(
                lambda dt, msgs=lines: self._add_log_batch(msgs),
                delay,
            )
            self._scheduled_events.append(ev)

        # Re-enable buttons after all steps
        ev = Clock.schedule_once(lambda dt: self._finish_training(), 5.3)
        self._scheduled_events.append(ev)

    def _add_log_batch(self, lines):
        for line in lines:
            self._add_log(line)

    def _finish_training(self):
        self._is_training = False
        self._train_btn.text = 'EXECUTE TRAINING PIPELINE'
        self._train_btn.disabled = False
        self._demo_btn.disabled = False
        self._compat_btn.disabled = False

    # ──────────────────────────────────────────────────────────
    # Compatibility Check
    # ──────────────────────────────────────────────────────────

    def _run_compat_check(self):
        """Run the compatibility diagnostic in a background-friendly way."""
        if self._is_training or self._is_checking:
            return

        self._is_checking = True
        self._compat_btn.text = 'RUNNING...'
        self._compat_btn.disabled = True
        self._train_btn.disabled = True
        self._demo_btn.disabled = True
        self._compat_label.text = 'Running diagnostic...\n'

        # Schedule the actual work for the next frame so the UI updates first
        Clock.schedule_once(lambda dt: self._do_compat_check(), 0.1)

    def _do_compat_check(self):
        """Execute the actual compatibility check."""
        try:
            from tools.compatibility_check import run_compatibility_check
            output = run_compatibility_check()
        except Exception as e:
            import traceback
            output = f'ERROR running compatibility check:\n{traceback.format_exc()}'

        self._compat_label.text = output
        self._is_checking = False
        self._compat_btn.text = 'RUN COMPATIBILITY CHECK'
        self._compat_btn.disabled = False
        self._train_btn.disabled = False
        self._demo_btn.disabled = False

    def _unschedule_all(self):
        for ev in self._scheduled_events:
            ev.cancel()
        self._scheduled_events.clear()

    def cleanup(self):
        """Cleanup scheduled events."""
        self._unschedule_all()
