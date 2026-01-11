import sys
import random
import requests
import re

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QComboBox, QProgressBar, QFrame,
    QMessageBox, QCheckBox, QLineEdit, QPlainTextEdit, QSizePolicy,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor


# ============================================================
# CONFIG: STATES, PHASES, MODES
# ============================================================

STATE_COLORS = {
    "Calm": "#2563eb",     # vivid blue
    "Stressed": "#ea0c0c", # vivid orange
    "Focused": "#16a34a",  # vivid green
}

STATE_CONFIG = {
    "Calm": {
        "description": "Box breathing and 4-7-8 breathing to induce a calm, relaxed state.",
        "phases": [
            {
                "name": "Box Breathing (4-4-4-4)",
                "duration_min": 10,
                "mode": "breathing",
                "breath_pattern": (4, 4, 4, 4),  # Inhale, Hold, Exhale, Hold
                "instructions": (
                    "Box Breathing\n\n"
                    "• Inhale for 4 seconds.\n"
                    "• Hold for 4 seconds.\n"
                    "• Exhale for 4 seconds.\n"
                    "• Hold for 4 seconds.\n\n"
                    "Follow the on-screen cues to effectively calm your nervous system."
                ),
            },
            {
                "name": "4-7-8 Breathing",
                "duration_min": 10,
                "mode": "breathing",
                "breath_pattern": (4, 7, 8, 0),  # Inhale, Hold, Exhale, Hold(0)
                "instructions": (
                    "4-7-8 Breathing\n\n"
                    "• Sit comfortably, back straight, feet flat.\n"
                    "• Close your eyes or keep them softly focused.\n"
                    "• Inhale through your nose for 4 seconds.\n"
                    "• Hold for 7 seconds.\n"
                    "• Exhale slowly through your mouth for 8 seconds.\n\n"
                    "Follow the on-screen breathing cue. Keep your head and jaw relaxed."
                ),
            },
        ],
    },

    "Stressed": {
        "description": "Cognitive stress using math, Stroop task, and listing challenges.",
        "phases": [
            {
                "name": "Rapid Mental Math",
                "duration_min": 4,
                "mode": "math",
                "instructions": (
                    "Rapid Mental Math\n\n"
                    "• Start at 1000.\n"
                    "• Keep subtracting 7 (1000, 993, 986, ...).\n"
                    "• You can type your answers quickly below to stay engaged.\n\n"
                    "Try to go as fast as you can. The app will check your answers."
                ),
            },
            {
                "name": "Stroop Task (Color-Word Conflict)",
                "duration_min": 8,
                "mode": "stroop",
                "instructions": (
                    "Stroop Task\n\n"
                    "• A color word will appear (e.g., RED, BLUE, GREEN).\n"
                    "• The ink color may NOT match the word meaning.\n"
                    "• Your task: Click the BUTTON that matches the INK COLOR, "
                    "not the word.\n\n"
                    "Example:\n"
                    "Word shows 'RED' in BLUE color → click 'Blue'."
                ),
            },
            {
                "name": "Timed Listing Challenges",
                "duration_min": 4,
                "mode": "listing",
                "instructions": (
                    "Listing Challenge\n\n"
                    "• For about a minute each, list as many items as you can:\n"
                    "  - Animals\n"
                    "  - Countries\n"
                    "  - Fruits\n"
                    "  - Sports\n\n"
                    "Type them quickly in the box below. Don't worry about spelling.\n"
                    "The time pressure + thinking keeps stress high."
                ),
            },
            {
                "name": "Rapid Addition (Add 7 from 0)",
                "duration_min": 4,
                "mode": "math",
                "math_operation": "add",
                "start_value": 0,
                "instructions": (
                    "Rapid Addition\n\n"
                    "• Start at 0.\n"
                    "• Keep adding 7 (0, 7, 14, ...).\n"
                    "• Try to beat your previous speed.\n"
                    "• If you want extra pressure, play a ticking or metronome sound "
                    "from your phone or PC.\n\n"
                    "Stay mentally engaged; the goal is cognitive stress."
                ),
            },
        ],
    },

    "Focused": {
        "description": "Sustained attention with technical reading and recall.",
        "phases": [
            {
                "name": "Focused Reading – Technical Article",
                "duration_min": 10,
                "mode": "reading",
                "instructions": (
                    "Focused Reading – Technical Content\n\n"
                    "• Read the technical article shown below.\n"
                    "• Aim to understand the key ideas.\n\n"
                    "Use 'Load New Article' to fetch a random technical topic.\n"
                    "Stay focused and avoid distractions while reading."
                ),
             },
            {
                "name": "Mental Recall & Summary",
                "duration_min": 10,
                "mode": "recall",
                "instructions": (
                    "Recall & Internal Summary\n\n"
                    "• Without loading new content, try to recall what you just read.\n"
                    "• In your mind or in the text box, summarize the main ideas.\n\n"
                    "You can type a short summary below if you want.\n"
                    "Focus on accuracy and structure."
                ),
            },
        ],
    },
}


def state_total_seconds(state_key: str) -> int:
    return sum(phase["duration_min"] * 60 for phase in STATE_CONFIG[state_key]["phases"])


def phase_seconds(state_key: str, index: int) -> int:
    return STATE_CONFIG[state_key]["phases"][index]["duration_min"] * 60


# ============================================================
# LOCAL ARTICLES (FALLBACK CONTENT FOR FOCUSED STATE)
# ============================================================

LOCAL_ARTICLES = [
    (
        "Neural network",
        "A neural network is a computational model inspired by the human brain. "
        "It consists of layers of interconnected nodes called neurons. Each neuron "
        "applies a weighted sum and a non-linear activation function. Neural networks "
        "are widely used for classification, regression, image recognition, and many "
        "other machine learning tasks."
    ),
    (
        "Microcontroller",
        "A microcontroller is a small computer on a single integrated circuit. It "
        "typically includes a processor core, memory, and programmable input-output "
        "peripherals. Microcontrollers are used in embedded systems for tasks such "
        "as sensor reading, motor control, and communication with other devices."
    ),
    (
        "Electroencephalography",
        "Electroencephalography, or EEG, is a non-invasive method for measuring the electrical "
        "activity of the brain using electrodes placed on the scalp. Each electrode records tiny "
        "voltage changes that arise when large groups of neurons become active together, especially "
        "pyramidal cells in the cortex. A single neuron produces a signal that is far too small to "
        "measure at the scalp, but when thousands of neurons fire in synchrony, their electrical "
        "fields add up and create a measurable signal that spreads through brain tissue, skull, and "
        "skin. EEG does not capture individual spikes the way an implanted microelectrode might, "
        "but instead reflects the summed postsynaptic potentials under each electrode. Because these "
        "potentials evolve very quickly, EEG can follow brain dynamics on the order of milliseconds, "
        "making it useful for studying fast cognitive processes and building real-time brain–computer "
        "interfaces."
    ),
    (
        "Quantum computing",
        "Quantum computing is a model of computation that uses quantum-mechanical phenomena such as "
        "superposition and entanglement to process information. Instead of classical bits that are "
        "strictly 0 or 1, a quantum computer uses qubits that can exist in a combination of states. "
        "By manipulating many qubits together, quantum algorithms can solve certain problems much "
        "more efficiently than known classical algorithms, such as factoring large numbers or simulating "
        "quantum systems."
    ),
]


# ============================================================
# WIKIPEDIA API HELPER – LONG TEXT, CLEANED
# ============================================================

def fetch_wikipedia_summary(topic: str, timeout_sec: int = 5, max_chars: int = 20000):
    """
    Fetch a *long* Wikipedia article as plain text and convert it into a
    single-paragraph, readable format.

    Returns (title, text) if successful, else (None, None).
    """
    try:
        url = "https://en.wikipedia.org/w/api.php"

        params = {
            "action": "query",
            "prop": "extracts",
            "explaintext": 1,      # plain text, no HTML
            "format": "json",
            "redirects": 1,
            "titles": topic,
        }

        headers = {
            "User-Agent": "BrainStateTrainer/1.0 (contact: example@example.com)"
        }

        resp = requests.get(url, params=params, headers=headers, timeout=timeout_sec)
        print("Wiki long status:", resp.status_code)

        if resp.status_code != 200:
            return None, None

        data = resp.json()
        query = data.get("query", {})
        pages = query.get("pages", {})

        if not pages:
            return None, None

        # pages is a dict keyed by pageid; take the first one
        page = next(iter(pages.values()))
        title = page.get("title")
        extract = page.get("extract", "")

        if not extract or len(extract.strip()) < 50:
            return None, None

        # Optional safety cap so it doesn't become a book
        if len(extract) > max_chars:
            extract = extract[:max_chars]

        # Remove headings like "== History =="
        extract = re.sub(r"^==.*?==\s*$", "", extract, flags=re.MULTILINE)

        # Split into non-empty lines, strip each
        lines = [line.strip() for line in extract.splitlines() if line.strip()]

        # Join into one long paragraph
        text = " ".join(lines)

        # Collapse multiple spaces
        text = " ".join(text.split())

        return title, text

    except Exception as e:
        print("Wiki exception:", e)
        return None, None


# ============================================================
# MAIN WINDOW
# ============================================================

class BrainStateApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Brain State Trainer – Calm / Stressed / Focused")
        self.setMinimumSize(1100, 620)

        # Runtime state
        self.current_state_key = "Calm"
        self.current_phase_index = 0

        self.state_elapsed_seconds = 0
        self.phase_remaining_seconds = phase_seconds(self.current_state_key, self.current_phase_index)

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.on_timer_tick)

        self.is_running = False
        self.auto_sequence = False

        # Scoring
        self.score_correct = 0
        self.score_attempts = 0

        # Breathing cycle timer (for guided breathing)
        self.breath_timer = QTimer(self)
        self.breath_timer.setInterval(1000)
        self.breath_timer.timeout.connect(self.on_breath_tick)
        self.breath_cycle_pos = 0
        self.current_breath_pattern = (4, 7, 8, 0) # Default
        self.breath_cycle_length = sum(self.current_breath_pattern)

        # Stroop state
        self.stroop_colors = [
            ("Red", "#dc2626"),
            ("Green", "#16a34a"),
            ("Blue", "#2563eb"),
            ("Yellow", "#eab308"),
            ("Black", "#111827"),
            ("Pink", "#db2777"),
        ]
        self.stroop_current_word = None
        self.stroop_current_color_name = None

        # Math state
        self.math_current_value = 1000

        # Reading state
        self.current_article_title = ""
        self.current_article_text = ""
        self.current_keyword = ""

        self._build_ui()
        self.apply_theme()
        self.update_ui_from_state()

    # --------------------------------------------------------
    # UI setup
    # --------------------------------------------------------
    def _build_ui(self):
        """Constructs the high-fidelity dashboard layout."""
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(30)
        central.setLayout(main_layout)

        # --- CENTRAL WORKSPACE (Glass Card) ---
        left_panel = QFrame()
        left_panel.setObjectName("MainGlassCard")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(40, 40, 40, 40)
        left_layout.setSpacing(25)
        main_layout.addWidget(left_panel, 3)

        self.label_state_title = QLabel("CALM")
        self.label_phase_title = QLabel("PHASE NAME")
        left_layout.addWidget(self.label_state_title)
        left_layout.addWidget(self.label_phase_title)

        # Dashboard HUD
        self.timer_container = QFrame()
        self.timer_container.setObjectName("TimerBox")
        timer_layout = QVBoxLayout(self.timer_container)
        self.label_timer = QLabel("20:00")
        self.label_timer.setAlignment(Qt.AlignCenter)
        timer_layout.addWidget(self.label_timer)
        left_layout.addWidget(self.timer_container)

        self.progress_state = QProgressBar()
        self.progress_state.setRange(0, 1000)
        self.progress_state.setFixedHeight(10)
        self.progress_state.setTextVisible(False)
        left_layout.addWidget(self.progress_state)

        self.label_breath_cue = QLabel("")
        self.label_breath_cue.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.label_breath_cue)

        # Task Execution Stack
        self.stack_layout = QVBoxLayout()
        left_layout.addLayout(self.stack_layout, 1)

        # Math Task UI
        self.widget_math = QWidget()
        math_l = QVBoxLayout(self.widget_math)
        self.label_math_current = QLabel("CURRENT SEED: 1000")
        self.edit_math_answer = QLineEdit()
        self.edit_math_answer.setPlaceholderText("Submit next in sequence...")
        self.edit_math_answer.setFixedHeight(50)
        self.edit_math_answer.returnPressed.connect(self.on_math_answer)
        self.label_math_feedback = QLabel("")
        math_l.addWidget(self.label_math_current)
        math_l.addWidget(self.edit_math_answer)
        math_l.addWidget(self.label_math_feedback)

        # Stroop Task UI (Modified for user request: Top Buttons)
        self.widget_stroop = QWidget()
        stroop_l = QVBoxLayout(self.widget_stroop)
        stroop_l.setSpacing(20)

        # Buttons placed at the top
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        self.stroop_buttons = []
        for name, color in self.stroop_colors:
            b = QPushButton(name)
            b.setObjectName("StroopButton")
            b.setCursor(Qt.PointingHandCursor)
            b.setFixedHeight(45)
            b.clicked.connect(self.on_stroop_button_clicked)
            b._color_name = name
            self.stroop_buttons.append(b)
            btn_row.addWidget(b)
        
        self.label_stroop_word = QLabel("WORD")
        self.label_stroop_word.setAlignment(Qt.AlignCenter)
        self.label_stroop_feedback = QLabel("")
        self.label_stroop_feedback.setAlignment(Qt.AlignCenter)
        
        stroop_l.addLayout(btn_row)
        stroop_l.addWidget(self.label_stroop_word)
        stroop_l.addWidget(self.label_stroop_feedback)

        # Listing Task UI
        self.widget_listing = QWidget()
        list_l = QVBoxLayout(self.widget_listing)
        self.label_listing_prompt = QLabel("Semantic Retrieval Task")
        self.text_listing = QPlainTextEdit()
        list_l.addWidget(self.label_listing_prompt)
        list_l.addWidget(self.text_listing)

        # Reading Task UI
        self.widget_reading = QWidget()
        read_l = QVBoxLayout(self.widget_reading)
        self.label_article_title = QLabel("ARTICLE")
        self.label_keyword = QLabel("")
        self.btn_load_article = QPushButton("LOAD CONTENT")
        self.btn_load_article.setFixedHeight(40)
        self.btn_load_article.clicked.connect(self.load_random_article)
        self.text_article = QTextEdit()
        self.text_article.setReadOnly(True)
        read_l.addWidget(self.label_article_title)
        read_l.addWidget(self.label_keyword)
        read_l.addWidget(self.btn_load_article)
        read_l.addWidget(self.text_article)

        # Recall UI
        self.widget_recall = QWidget()
        rec_l = QVBoxLayout(self.widget_recall)
        self.label_recall_hint = QLabel("Working Memory Synthesis")
        self.text_recall = QPlainTextEdit()
        rec_l.addWidget(self.label_recall_hint)
        rec_l.addWidget(self.text_recall)

        self.stack_layout.addWidget(self.widget_math)
        self.stack_layout.addWidget(self.widget_stroop)
        self.stack_layout.addWidget(self.widget_listing)
        self.stack_layout.addWidget(self.widget_reading)
        self.stack_layout.addWidget(self.widget_recall)

        self.text_instructions = QTextEdit()
        self.text_instructions.setReadOnly(True)
        self.text_instructions.setFixedHeight(140)
        left_layout.addWidget(self.text_instructions)

        self.label_state_description = QLabel("")
        self.label_state_description.setWordWrap(True)
        left_layout.addWidget(self.label_state_description)

        # --- SIDEBAR CONTROL PANEL ---
        right_panel = QFrame()
        right_panel.setObjectName("ControlGlassCard")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(30, 45, 30, 45)
        right_layout.setSpacing(18)
        main_layout.addWidget(right_panel, 1)

        right_layout.addWidget(QLabel("SYSTEM CONTEXT"))
        self.combo_state = QComboBox()
        for k in STATE_CONFIG.keys(): self.combo_state.addItem(k)
        self.combo_state.currentTextChanged.connect(self.on_state_changed)
        right_layout.addWidget(self.combo_state)

        self.checkbox_auto_sequence = QCheckBox("Sequential Protocol")
        self.checkbox_auto_sequence.stateChanged.connect(self.on_auto_sequence_toggled)
        right_layout.addWidget(self.checkbox_auto_sequence)

        line = QFrame(); line.setFrameShape(QFrame.HLine); line.setObjectName("Divider")
        right_layout.addWidget(line)

        self.btn_start = QPushButton("INITIALIZE")
        self.btn_pause = QPushButton("PAUSE")
        self.btn_reset = QPushButton("TERMINATE")
        self.btn_next_phase = QPushButton("INCREMENT PHASE")

        self.btn_start.clicked.connect(self.on_start_clicked)
        self.btn_pause.clicked.connect(self.on_pause_clicked)
        self.btn_reset.clicked.connect(self.on_reset_clicked)
        self.btn_next_phase.clicked.connect(self.on_next_phase_clicked)

        for b in (self.btn_start, self.btn_pause, self.btn_reset, self.btn_next_phase):
            b.setFixedHeight(50)
            b.setCursor(Qt.PointingHandCursor)
            right_layout.addWidget(b)

        right_layout.addStretch()
        self.label_help = QLabel("Select a protocol state to begin baseline training.")
        self.label_help.setWordWrap(True)
        right_layout.addWidget(self.label_help)

    def apply_theme(self):
        """Applies the dark-cyber glassmorphism visual styles."""
        self.setStyleSheet("""
            QMainWindow { background-color: #05070a; font-family: 'Inter', 'Segoe UI', sans-serif; }
            
            QFrame#MainGlassCard, QFrame#ControlGlassCard {
                background-color: rgba(15, 20, 30, 0.8);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 24px;
            }

            QFrame#TimerBox {
                background-color: rgba(0, 0, 0, 0.4);
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.03);
            }

            QLabel { color: #cbd5e1; font-size: 14px; }
            
            QLineEdit, QTextEdit, QPlainTextEdit {
                background-color: rgba(0, 0, 0, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 14px;
                color: #f1f5f9;
                font-size: 14px;
            }

            QComboBox {
                background-color: rgba(0, 0, 0, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 10px;
                color: #ffffff;
            }

            QProgressBar {
                background-color: rgba(255, 255, 255, 0.03);
                border-radius: 5px;
            }

            QCheckBox { color: #64748b; font-weight: bold; }

            QPushButton {
                background-color: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 12px;
                color: #ffffff;
                font-weight: 800;
                letter-spacing: 1.5px;
                text-transform: uppercase;
            }

            QPushButton#StroopButton {
                background-color: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.15);
                color: #ffffff;
                font-size: 11px;
            }

            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-color: rgba(255, 255, 255, 0.4);
            }

            QFrame#Divider { background-color: rgba(255, 255, 255, 0.1); min-height: 1px; }
        """)

        self.label_state_title.setStyleSheet("font-size: 44px; font-weight: 900; letter-spacing: 3px; color: #ffffff;")
        self.label_phase_title.setStyleSheet("font-size: 14px; color: #475569; font-weight: 800; text-transform: uppercase; letter-spacing: 1px;")
        self.label_timer.setStyleSheet("font-size: 85px; font-weight: 900; color: #ffffff; font-family: 'JetBrains Mono', 'Consolas';")
        self.label_breath_cue.setStyleSheet("font-size: 40px; font-weight: 900;")
        self.label_state_description.setStyleSheet("color: #64748b; font-style: italic; line-height: 1.6; font-size: 13px;")
        
        self.btn_start.setStyleSheet("background-color: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.3); font-size: 16px;")

        self.apply_accent_color(STATE_COLORS.get(self.current_state_key, "#2563eb"))

    def apply_accent_color(self, color):
        """Updates the neon accent colors based on current state."""
        self.progress_state.setStyleSheet(f"QProgressBar::chunk {{ background-color: {color}; border-radius: 5px; }}")
        # Ensure we don't accidentally send None
        if not color: color = "#2563eb"
        
        self.label_state_title.setStyleSheet(f"font-size: 44px; font-weight: 900; letter-spacing: 3px; color: {color};")
        self.label_breath_cue.setStyleSheet(f"font-size: 40px; font-weight: 900; color: {color};")
        self.label_keyword.setStyleSheet(f"font-weight: 900; color: {color}; font-size: 18px; text-transform: uppercase;")

        # Dashboard Underglow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(color))
        self.timer_container.setGraphicsEffect(shadow)

        # Primary Button Glow
        btn_shadow = QGraphicsDropShadowEffect()
        btn_shadow.setBlurRadius(20)
        btn_shadow.setColor(QColor(color))
        self.btn_start.setGraphicsEffect(btn_shadow)
        # Stroop buttons need their own logic, so we don't touch them here globally 
        # (they are styled in creation, but maybe we should update them? They are colored by name so ok)

        # Focus ring for inputs
        self.edit_math_answer.setStyleSheet(f"""
            QLineEdit {{
                background-color: #0f1420;
                border: 2px solid #2d3748;
                border-radius: 20px;
                padding: 12px 16px;
                color: #f3f4f6;
                font-size: 15px;
            }}
            QLineEdit:focus {{
                border: 2px solid {color};
            }}
        """)

    # --------------------------------------------------------
    # State / phase changes & controls
    # --------------------------------------------------------
    def on_state_changed(self, new_state: str):
        if self.is_running:
            reply = QMessageBox.question(
                self,
                "Switch State?",
                "Timer is running. Switch state and reset?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                self.combo_state.blockSignals(True)
                self.combo_state.setCurrentText(self.current_state_key)
                self.combo_state.blockSignals(False)
                return

        self.current_state_key = new_state
        self.current_phase_index = 0
        self.state_elapsed_seconds = 0
        self.phase_remaining_seconds = phase_seconds(self.current_state_key, self.current_phase_index)
        self.is_running = False
        self.timer.stop()
        self.breath_timer.stop()
        
        # Reset scoring on state change
        self.score_correct = 0
        self.score_attempts = 0
        
        self.math_current_value = 1000  # reset math on state change
        self.update_ui_from_state()

    def on_auto_sequence_toggled(self, state):
        self.auto_sequence = (state == Qt.Checked)

    def on_start_clicked(self):
        if not self.is_running:
            self.is_running = True
            self.timer.start()
            phase = self._current_phase()
            if phase["mode"] == "breathing":
                self.breath_timer.start()

    def on_pause_clicked(self):
        if self.is_running:
            self.is_running = False
            self.timer.stop()
            self.breath_timer.stop()

    def on_reset_clicked(self):
        self.is_running = False
        self.timer.stop()
        self.breath_timer.stop()
        self.state_elapsed_seconds = 0
        self.current_phase_index = 0
        self.phase_remaining_seconds = phase_seconds(self.current_state_key, self.current_phase_index)
        self.math_current_value = 1000
        self.update_ui_from_state()

    def on_next_phase_clicked(self):
        cfg = STATE_CONFIG[self.current_state_key]
        if self.current_phase_index < len(cfg["phases"]) - 1:
            self.current_phase_index += 1
            self.phase_remaining_seconds = phase_seconds(self.current_state_key, self.current_phase_index)
            self.state_elapsed_seconds = sum(
                phase["duration_min"] * 60 for phase in cfg["phases"][:self.current_phase_index]
            )
            self.update_ui_from_state()
        else:
            QMessageBox.information(self, "End of State", "Already at last phase of this state.")

    # --------------------------------------------------------
    # Timer / breathing
    # --------------------------------------------------------
    def on_timer_tick(self):
        if not self.is_running:
            return

        if self.phase_remaining_seconds > 0:
            self.phase_remaining_seconds -= 1
            self.state_elapsed_seconds += 1
            self.update_timer_display()
        else:
            cfg = STATE_CONFIG[self.current_state_key]
            if self.current_phase_index < len(cfg["phases"]) - 1:
                self.current_phase_index += 1
                self.phase_remaining_seconds = phase_seconds(self.current_state_key, self.current_phase_index)
                self.update_ui_from_state()
            else:
                self.timer.stop()
                self.breath_timer.stop()
                self.is_running = False
                self.update_timer_display()
                
                msg = f"{self.current_state_key} session completed."
                if self.current_state_key == "Stressed":
                    msg += f"\n\nPerformance Score: {self.score_correct}/{self.score_attempts}"
                    if self.score_attempts > 0:
                        percent = int((self.score_correct / self.score_attempts) * 100)
                        msg += f" ({percent}%)"
                        if percent > 80:
                            msg += "\nGreat focus under pressure!"
                        else:
                            msg += "\nKeep practicing to improve resilience."
                
                QMessageBox.information(self, "State Complete", msg)
                if self.auto_sequence:
                    self._go_to_next_state_in_sequence()

    def on_breath_tick(self):
        phase = self._current_phase()
        if phase["mode"] != "breathing":
            self.label_breath_cue.setText("")
            return

        self.breath_cycle_pos = (self.breath_cycle_pos + 1) % self.breath_cycle_length
        t = self.breath_cycle_pos
        
        p1, p2, p3, p4 = self.current_breath_pattern
        
        if t < p1:
            self.label_breath_cue.setText(f"Inhale ({p1 - t})")
        elif t < p1 + p2:
            self.label_breath_cue.setText(f"Hold ({p1 + p2 - t})")
        elif t < p1 + p2 + p3:
            self.label_breath_cue.setText(f"Exhale ({p1 + p2 + p3 - t})")
        else:
             self.label_breath_cue.setText(f"Hold ({self.breath_cycle_length - t})")

    def _go_to_next_state_in_sequence(self):
        keys = list(STATE_CONFIG.keys())
        idx = keys.index(self.current_state_key)
        if idx < len(keys) - 1:
            next_state = keys[idx + 1]
            self.combo_state.setCurrentText(next_state)
        else:
            QMessageBox.information(self, "Sequence Complete",
                                    "All states (Calm → Stressed → Focused) completed.")

    # --------------------------------------------------------
    # UI updates
    # --------------------------------------------------------
    def _current_phase(self):
        return STATE_CONFIG[self.current_state_key]["phases"][self.current_phase_index]

    def update_ui_from_state(self):
        cfg = STATE_CONFIG[self.current_state_key]
        phase = self._current_phase()

        self.label_state_title.setText(self.current_state_key)
        self.label_phase_title.setText(phase["name"])
        self.text_instructions.setPlainText(phase["instructions"])
        self.label_state_description.setText(cfg["description"])

        accent = STATE_COLORS.get(self.current_state_key, "#2563eb")
        self.apply_accent_color(accent)

        self.combo_state.blockSignals(True)
        self.combo_state.setCurrentText(self.current_state_key)
        self.combo_state.blockSignals(False)

        # Reset widgets
        self.label_breath_cue.setText("")
        self.label_math_feedback.setText("")
        self.label_math_current.setText(f"Current number: {self.math_current_value}")
        self.edit_math_answer.clear()
        self.label_stroop_feedback.setText("")
        self.text_listing.clear()
        self.label_keyword.setText("")
        self.text_recall.clear()

        self.breath_timer.stop()
        if phase["mode"] == "breathing":
            # Update breath pattern for this phase
            pat = phase.get("breath_pattern", (4, 7, 8, 0))
            self.current_breath_pattern = pat
            self.breath_cycle_length = sum(pat)
            self.breath_cycle_pos = 0 # Restart cycle
            
            if self.is_running:
                self.breath_timer.start()

        # Show/hide interactive widgets based on mode
        mode = phase["mode"]
        self.widget_math.hide()
        self.widget_stroop.hide()
        self.widget_listing.hide()
        self.widget_reading.hide()
        self.widget_recall.hide()

        if mode == "breathing":
            pass
        elif mode == "math":
            # Check for start value override (e.g. switching to addition starting at 0)
            start_val = phase.get("start_value")
            if start_val is not None:
                # Force reset if the current value is completely different (e.g. carrying over from previous phase)
                # Since update_ui_from_state is called on phase transition, this is safe.
                # We simply force it to the start value to ensure the user starts fresh.
                 self.math_current_value = start_val
                 self.label_math_current.setText(f"Current number: {self.math_current_value}")
                 self.edit_math_answer.clear()
                 self.label_math_feedback.setText("")

            self.widget_math.show()
        elif mode == "stroop":
            self.widget_stroop.show()
            self.next_stroop_trial()
        elif mode == "listing":
            self.widget_listing.show()
        elif mode == "reading":
            self.widget_reading.show()
            if not self.current_article_text:
                self.load_random_article()
        elif mode == "reading_keyword":
            self.widget_reading.show()
            if not self.current_article_text:
                self.load_random_article()
            self.pick_keyword_for_article()
        elif mode == "recall":
            self.widget_recall.show()

        self.update_timer_display()

    def update_timer_display(self):
        # Display PHASE remaining time, not total state time
        minutes = self.phase_remaining_seconds // 60
        seconds = self.phase_remaining_seconds % 60
        self.label_timer.setText(f"{minutes:02d}:{seconds:02d}")

        # Progress bar still tracks TOTAL state progress
        total_state = state_total_seconds(self.current_state_key)
        if total_state > 0:
            progress = int((self.state_elapsed_seconds / total_state) * 1000)
        else:
            progress = 0
        self.progress_state.setValue(progress)

    # --------------------------------------------------------
    # Math logic
    # --------------------------------------------------------
    def on_math_answer(self):
        text = self.edit_math_answer.text().strip()
        if not text:
            return
        try:
            value = int(text)
        except ValueError:
            self.label_math_feedback.setText("Please enter a number.")
            return

        # Determine operation
        phase = self._current_phase()
        op = phase.get("math_operation", "subtract")
        
        if op == "add":
             expected = self.math_current_value + 7
        else:
             expected = self.math_current_value - 7
             
        self.score_attempts += 1
        if value == expected:
            self.score_correct += 1
            self.math_current_value = value
            self.label_math_current.setText(f"Current number: {self.math_current_value}")
            self.label_math_feedback.setText("Correct, keep going!")
            self.edit_math_answer.clear()
        else:
            self.label_math_feedback.setText(f"Wrong, expected {expected}. Try again.")

    # --------------------------------------------------------
    # Stroop logic
    # --------------------------------------------------------
    def next_stroop_trial(self):
        words = [c[0] for c in self.stroop_colors]
        word = random.choice(words)
        color_name, color_hex = random.choice(self.stroop_colors)

        if random.random() < 0.7:
            choices = [c for c in self.stroop_colors if c[0] != word]
            color_name, color_hex = random.choice(choices)

        self.stroop_current_word = word
        self.stroop_current_color_name = color_name

        self.label_stroop_word.setText(word)
        self.label_stroop_word.setStyleSheet(
            f"font-size: 40px; font-weight: 700; padding: 10px; color: {color_hex};"
        )
        self.label_stroop_feedback.setText("Pick the INK color, not the word.")

    def on_stroop_button_clicked(self):
        sender = self.sender()
        chosen_color = getattr(sender, "_color_name", None)
        if not chosen_color:
            return

        self.score_attempts += 1
        if chosen_color == self.stroop_current_color_name:
            self.score_correct += 1
            self.label_stroop_feedback.setText("Correct! Next...")
        else:
            self.label_stroop_feedback.setText(
                f"Wrong. The ink color was {self.stroop_current_color_name}."
            )
        self.next_stroop_trial()

    # --------------------------------------------------------
    # Reading / API logic
    # --------------------------------------------------------
    def load_random_article(self):
        """Fetch random technical-ish article. Uses local text + optional Wikipedia API."""
        local_title, local_text = random.choice(LOCAL_ARTICLES)
        title = f"{local_title} (Local)"
        text = local_text

        wiki_title, wiki_text = fetch_wikipedia_summary(local_title)
        if wiki_title and wiki_text:
            title = f"{wiki_title} (Wikipedia)"
            text = wiki_text

        self.current_article_title = title
        self.current_article_text = text
        self.label_article_title.setText(self.current_article_title)
        self.text_article.setPlainText(self.current_article_text)
        self.label_keyword.setText("")

    def pick_keyword_for_article(self):
        if not self.current_article_text:
            return

        words = [w.strip(".,()[]:;\"'").lower() for w in self.current_article_text.split()]
        candidates = [w for w in words if len(w) > 4]
        if not candidates:
            candidates = [w for w in words if len(w) > 3]
        if not candidates:
            candidates = words

        if not candidates:
            self.current_keyword = ""
            self.label_keyword.setText("")
            return

        self.current_keyword = random.choice(candidates)
        self.label_keyword.setText(f"Track this keyword: \"{self.current_keyword}\"")


# ============================================================
# MAIN
# ============================================================

def main():
    app = QApplication(sys.argv)
    window = BrainStateApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
