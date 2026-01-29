import 'package:flutter/material.dart';

/// Phase modes for calibration tasks
enum PhaseMode {
  breathing,
  math,
  stroop,
  listing,
  reading,
  recall,
}

/// Math operation types
enum MathOp { add, subtract }

/// Single calibration phase configuration
class PhaseConfig {
  final String name;
  final int durationMinutes;
  final PhaseMode mode;
  final String instructions;
  
  // Breathing-specific
  final List<int>? breathPattern; // [Inhale, Hold, Exhale, Hold]
  
  // Math-specific
  final MathOp? mathOperation;
  final int? startValue;
  final int stepValue;
  
  // Stroop-specific
  final List<MapEntry<String, Color>>? stroopColors;
  
  // Listing-specific
  final List<String>? listingCategories;

  const PhaseConfig({
    required this.name,
    required this.durationMinutes,
    required this.mode,
    required this.instructions,
    this.breathPattern,
    this.mathOperation,
    this.startValue,
    this.stepValue = 7,
    this.stroopColors,
    this.listingCategories,
  });
  
  /// Get phase duration in seconds
  int get durationSeconds => durationMinutes * 60;
}

/// State configuration (Calm, Stressed, Focused)
class StateConfig {
  final Color color;
  final String description;
  final List<PhaseConfig> phases;

  const StateConfig({
    required this.color,
    required this.description,
    required this.phases,
  });
  
  /// Total duration of all phases in seconds
  int get totalSeconds => phases.fold(0, (sum, p) => sum + p.durationSeconds);
}

/// Default Stroop colors used across the app
const List<MapEntry<String, Color>> defaultStroopColors = [
  MapEntry('Red', Color(0xFFDC2626)),
  MapEntry('Green', Color(0xFF16A34A)),
  MapEntry('Blue', Color(0xFF2563EB)),
  MapEntry('Yellow', Color(0xFFEAB308)),
  MapEntry('Black', Color(0xFF111827)),
  MapEntry('Pink', Color(0xFFDB2777)),
];

/// Complete state configuration - ported from Python calibration app
final Map<String, StateConfig> stateConfig = {
  'Calm': StateConfig(
    color: const Color(0xFF2563EB), // Vivid blue
    description: 'Box breathing and 4-7-8 breathing to induce a calm, relaxed state.',
    phases: [
      PhaseConfig(
        name: 'Box Breathing (4-4-4-4)',
        durationMinutes: 10,
        mode: PhaseMode.breathing,
        breathPattern: [4, 4, 4, 4], // Inhale, Hold, Exhale, Hold
        instructions: '''Box Breathing

• Inhale for 4 seconds.
• Hold for 4 seconds.
• Exhale for 4 seconds.
• Hold for 4 seconds.

Follow the on-screen cues to effectively calm your nervous system.''',
      ),
      PhaseConfig(
        name: '4-7-8 Breathing',
        durationMinutes: 10,
        mode: PhaseMode.breathing,
        breathPattern: [4, 7, 8, 0], // Inhale, Hold, Exhale, Hold(0)
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
    color: const Color(0xFFEA0C0C), // Vivid red
    description: 'Cognitive stress using math, Stroop task, and listing challenges.',
    phases: [
      PhaseConfig(
        name: 'Rapid Mental Math',
        durationMinutes: 4,
        mode: PhaseMode.math,
        mathOperation: MathOp.subtract,
        startValue: 1000,
        stepValue: 7,
        instructions: '''Rapid Mental Math

• Start at 1000.
• Keep subtracting 7 (1000, 993, 986, ...).
• You can type your answers quickly below to stay engaged.

Try to go as fast as you can. The app will check your answers.''',
      ),
      PhaseConfig(
        name: 'Stroop Task (Color-Word Conflict)',
        durationMinutes: 8,
        mode: PhaseMode.stroop,
        stroopColors: defaultStroopColors,
        instructions: '''Stroop Task

• A color word will appear (e.g., RED, BLUE, GREEN).
• The ink color may NOT match the word meaning.
• Your task: Click the BUTTON that matches the INK COLOR, not the word.

Example:
Word shows 'RED' in BLUE color → click 'Blue'.''',
      ),
      PhaseConfig(
        name: 'Timed Listing Challenges',
        durationMinutes: 4,
        mode: PhaseMode.listing,
        listingCategories: ['Animals', 'Countries', 'Fruits', 'Sports'],
        instructions: '''Listing Challenge

• For about a minute each, list as many items as you can:
  - Animals
  - Countries
  - Fruits
  - Sports

Type them quickly in the box below. Don't worry about spelling.
The time pressure + thinking keeps stress high.''',
      ),
      PhaseConfig(
        name: 'Rapid Addition (Add 7 from 0)',
        durationMinutes: 4,
        mode: PhaseMode.math,
        mathOperation: MathOp.add,
        startValue: 0,
        stepValue: 7,
        instructions: '''Rapid Addition

• Start at 0.
• Keep adding 7 (0, 7, 14, ...).
• Try to beat your previous speed.
• If you want extra pressure, play a ticking or metronome sound from your phone or PC.

Stay mentally engaged; the goal is cognitive stress.''',
      ),
    ],
  ),
  
  'Focused': StateConfig(
    color: const Color(0xFF16A34A), // Vivid green
    description: 'Sustained attention with technical reading and recall.',
    phases: [
      PhaseConfig(
        name: 'Focused Reading – Technical Article',
        durationMinutes: 10,
        mode: PhaseMode.reading,
        instructions: '''Focused Reading – Technical Content

• Read the technical article shown below.
• Aim to understand the key ideas.

Use 'Load New Article' to fetch a random technical topic.
Stay focused and avoid distractions while reading.''',
      ),
      PhaseConfig(
        name: 'Mental Recall & Summary',
        durationMinutes: 10,
        mode: PhaseMode.recall,
        instructions: '''Recall & Internal Summary

• Without loading new content, try to recall what you just read.
• In your mind or in the text box, summarize the main ideas.

You can type a short summary below if you want.
Focus on accuracy and structure.''',
      ),
    ],
  ),
};

/// Get state color by name
Color getStateColor(String stateName) {
  return stateConfig[stateName]?.color ?? const Color(0xFF2563EB);
}
