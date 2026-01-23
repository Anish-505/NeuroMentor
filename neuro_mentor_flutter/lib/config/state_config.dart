/// NeuroMentor Flutter App - State Configuration
/// Port of the Python STATE_CONFIG from calibration_final.py

class Phase {
  final String name;
  final int durationMinutes;
  final String mode;
  final String instructions;
  final List<int>? breathPattern; // For breathing exercises: [inhale, hold, exhale, hold]
  final String? mathOperation;
  final int? startValue;

  const Phase({
    required this.name,
    required this.durationMinutes,
    required this.mode,
    required this.instructions,
    this.breathPattern,
    this.mathOperation,
    this.startValue,
  });

  int get durationSeconds => durationMinutes * 60;
}

class StateConfig {
  final String name;
  final String description;
  final String color;
  final List<Phase> phases;

  const StateConfig({
    required this.name,
    required this.description,
    required this.color,
    required this.phases,
  });

  int get totalSeconds => phases.fold(0, (sum, p) => sum + p.durationSeconds);
}

// State Colors matching the Python original
class StateColors {
  static const String calm = '#2563eb';     // vivid blue
  static const String stressed = '#ea0c0c'; // vivid red
  static const String focused = '#16a34a';  // vivid green
}

// Full state configurations matching Python calibration_final.py
final Map<String, StateConfig> stateConfigs = {
  'Calm': StateConfig(
    name: 'Calm',
    description: 'Box breathing and 4-7-8 breathing to induce a calm, relaxed state.',
    color: StateColors.calm,
    phases: [
      Phase(
        name: 'Box Breathing (4-4-4-4)',
        durationMinutes: 10,
        mode: 'breathing',
        breathPattern: [4, 4, 4, 4],
        instructions: '''Box Breathing

• Inhale for 4 seconds.
• Hold for 4 seconds.
• Exhale for 4 seconds.
• Hold for 4 seconds.

Follow the on-screen cues to effectively calm your nervous system.''',
      ),
      Phase(
        name: '4-7-8 Breathing',
        durationMinutes: 10,
        mode: 'breathing',
        breathPattern: [4, 7, 8, 0],
        instructions: '''4-7-8 Breathing

• Sit comfortably, back straight, feet flat.
• Close your eyes or keep them softly focused.
• Inhale through your nose for 4 seconds.
• Hold for 7 seconds.
• Exhale slowly through your mouth for 8 seconds.

Follow the on-screen breathing cue. Keep your head and jaw relaxed.''',
      ),
    ],
  ),
  'Stressed': StateConfig(
    name: 'Stressed',
    description: 'Cognitive stress using math, Stroop task, and listing challenges.',
    color: StateColors.stressed,
    phases: [
      Phase(
        name: 'Rapid Mental Math',
        durationMinutes: 4,
        mode: 'math',
        mathOperation: 'subtract',
        startValue: 1000,
        instructions: '''Rapid Mental Math

• Start at 1000.
• Keep subtracting 7 (1000, 993, 986, ...).
• You can type your answers quickly below to stay engaged.

Try to go as fast as you can. The app will check your answers.''',
      ),
      Phase(
        name: 'Stroop Task (Color-Word Conflict)',
        durationMinutes: 8,
        mode: 'stroop',
        instructions: '''Stroop Task

• A color word will appear (e.g., RED, BLUE, GREEN).
• The ink color may NOT match the word meaning.
• Your task: Tap the BUTTON that matches the INK COLOR, not the word.

Example:
Word shows 'RED' in BLUE color → tap 'Blue'.''',
      ),
      Phase(
        name: 'Timed Listing Challenges',
        durationMinutes: 4,
        mode: 'listing',
        instructions: '''Listing Challenge

• For about a minute each, list as many items as you can:
  - Animals
  - Countries
  - Fruits
  - Sports

Type them quickly in the box below. Don't worry about spelling.
The time pressure + thinking keeps stress high.''',
      ),
      Phase(
        name: 'Rapid Addition (Add 7 from 0)',
        durationMinutes: 4,
        mode: 'math',
        mathOperation: 'add',
        startValue: 0,
        instructions: '''Rapid Addition

• Start at 0.
• Keep adding 7 (0, 7, 14, ...).
• Try to beat your previous speed.

Stay mentally engaged; the goal is cognitive stress.''',
      ),
    ],
  ),
  'Focused': StateConfig(
    name: 'Focused',
    description: 'Sustained attention with technical reading and recall.',
    color: StateColors.focused,
    phases: [
      Phase(
        name: 'Focused Reading – Technical Article',
        durationMinutes: 10,
        mode: 'reading',
        instructions: '''Focused Reading – Technical Content

• Read the technical article shown below.
• Aim to understand the key ideas.

Use 'Load New Article' to fetch a random technical topic.
Stay focused and avoid distractions while reading.''',
      ),
      Phase(
        name: 'Mental Recall & Summary',
        durationMinutes: 10,
        mode: 'recall',
        instructions: '''Recall & Internal Summary

• Without loading new content, try to recall what you just read.
• In your mind or in the text box, summarize the main ideas.

You can type a short summary below if you want.
Focus on accuracy and structure.''',
      ),
    ],
  ),
};

// Local fallback articles for Focused state
final List<Map<String, String>> localArticles = [
  {
    'title': 'Neural network',
    'text': '''A neural network is a computational model inspired by the human brain. It consists of layers of interconnected nodes called neurons. Each neuron applies a weighted sum and a non-linear activation function. Neural networks are widely used for classification, regression, image recognition, and many other machine learning tasks.''',
  },
  {
    'title': 'Microcontroller',
    'text': '''A microcontroller is a small computer on a single integrated circuit. It typically includes a processor core, memory, and programmable input-output peripherals. Microcontrollers are used in embedded systems for tasks such as sensor reading, motor control, and communication with other devices.''',
  },
  {
    'title': 'Electroencephalography',
    'text': '''Electroencephalography, or EEG, is a non-invasive method for measuring the electrical activity of the brain using electrodes placed on the scalp. Each electrode records tiny voltage changes that arise when large groups of neurons become active together, especially pyramidal cells in the cortex. A single neuron produces a signal that is far too small to measure at the scalp, but when thousands of neurons fire in synchrony, their electrical fields add up and create a measurable signal that spreads through brain tissue, skull, and skin. EEG does not capture individual spikes the way an implanted microelectrode might, but instead reflects the summed postsynaptic potentials under each electrode. Because these potentials evolve very quickly, EEG can follow brain dynamics on the order of milliseconds, making it useful for studying fast cognitive processes and building real-time brain–computer interfaces.''',
  },
  {
    'title': 'Quantum computing',
    'text': '''Quantum computing is a model of computation that uses quantum-mechanical phenomena such as superposition and entanglement to process information. Instead of classical bits that are strictly 0 or 1, a quantum computer uses qubits that can exist in a combination of states. By manipulating many qubits together, quantum algorithms can solve certain problems much more efficiently than known classical algorithms, such as factoring large numbers or simulating quantum systems.''',
  },
];

// Stroop colors for the Stroop task
final List<Map<String, dynamic>> stroopColors = [
  {'name': 'Red', 'color': 0xFFdc2626},
  {'name': 'Green', 'color': 0xFF16a34a},
  {'name': 'Blue', 'color': 0xFF2563eb},
  {'name': 'Yellow', 'color': 0xFFeab308},
  {'name': 'Black', 'color': 0xFF111827},
  {'name': 'Pink', 'color': 0xFFdb2777},
];
