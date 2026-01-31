import 'dart:async';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../config/theme.dart';

/// Live EEG monitoring screen with real-time graphs
class MonitoringScreen extends StatefulWidget {
  const MonitoringScreen({super.key});

  @override
  State<MonitoringScreen> createState() => _MonitoringScreenState();
}

class _MonitoringScreenState extends State<MonitoringScreen> {
  Timer? _timer;
  int _seconds = 0;
  bool _running = false;
  String _state = 'Ready';
  
  final List<FlSpot> _focusData = [];
  final List<FlSpot> _stressData = [];
  double _currentFocus = 0.5;
  double _currentStress = 0.3;

  // EEG band powers
  double _delta = 0.2;
  double _theta = 0.3;
  double _alpha = 0.5;
  double _beta = 0.4;
  double _gamma = 0.2;

  void _start() {
    setState(() {
      _running = true;
      _focusData.clear();
      _stressData.clear();
      _seconds = 0;
    });
    
    _timer = Timer.periodic(const Duration(seconds: 1), (_) {
      _updateData();
    });
  }

  void _stop() {
    _timer?.cancel();
    setState(() {
      _running = false;
      _state = 'Stopped';
    });
  }

  void _updateData() {
    final random = Random();
    
    // Simulate EEG band changes
    _delta = (_delta + (random.nextDouble() - 0.5) * 0.1).clamp(0.1, 0.5);
    _theta = (_theta + (random.nextDouble() - 0.5) * 0.1).clamp(0.2, 0.6);
    _alpha = (_alpha + (random.nextDouble() - 0.5) * 0.1).clamp(0.3, 0.8);
    _beta = (_beta + (random.nextDouble() - 0.5) * 0.1).clamp(0.2, 0.7);
    _gamma = (_gamma + (random.nextDouble() - 0.5) * 0.1).clamp(0.1, 0.4);

    // Calculate focus (alpha/theta ratio)
    _currentFocus = (_alpha / _theta).clamp(0.0, 1.0);
    
    // Calculate stress (beta/alpha ratio)  
    _currentStress = (_beta / _alpha * 0.5).clamp(0.0, 1.0);

    // Determine state
    if (_currentFocus > 0.7) {
      _state = 'Focused';
    } else if (_currentStress > 0.6) {
      _state = 'Stressed';
    } else if (_currentFocus > 0.4) {
      _state = 'Calm';
    } else {
      _state = 'Unfocused';
    }

    setState(() {
      _seconds++;
      
      // Keep last 60 seconds of data
      if (_focusData.length >= 60) {
        _focusData.removeAt(0);
        _stressData.removeAt(0);
        // Shift x values
        for (int i = 0; i < _focusData.length; i++) {
          _focusData[i] = FlSpot(i.toDouble(), _focusData[i].y);
          _stressData[i] = FlSpot(i.toDouble(), _stressData[i].y);
        }
      }
      
      _focusData.add(FlSpot(_focusData.length.toDouble(), _currentFocus * 100));
      _stressData.add(FlSpot(_stressData.length.toDouble(), _currentStress * 100));
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Color get _stateColor {
    switch (_state) {
      case 'Focused':
        return Colors.green;
      case 'Stressed':
        return Colors.red;
      case 'Calm':
        return Colors.blue;
      default:
        return Colors.orange;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(gradient: AppTheme.backgroundGradient),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              children: [
                // Header
                Row(
                  children: [
                    IconButton(
                      onPressed: () => Navigator.pop(context),
                      icon: const Icon(Icons.arrow_back),
                    ),
                    const Spacer(),
                    // Timer
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                      decoration: glassDecoration(),
                      child: Text(
                        '${(_seconds ~/ 60).toString().padLeft(2, '0')}:${(_seconds % 60).toString().padLeft(2, '0')}',
                        style: const TextStyle(fontSize: 18, fontFamily: 'monospace'),
                      ),
                    ),
                    const Spacer(),
                    // State badge
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                      decoration: BoxDecoration(
                        color: _stateColor.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: _stateColor.withOpacity(0.5)),
                      ),
                      child: Text(
                        _state,
                        style: TextStyle(color: _stateColor, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 20),
                // Focus gauge
                Row(
                  children: [
                    Expanded(child: _buildGauge('Focus', _currentFocus, Colors.green)),
                    const SizedBox(width: 16),
                    Expanded(child: _buildGauge('Stress', _currentStress, Colors.red)),
                  ],
                ),
                const SizedBox(height: 20),
                // Focus graph
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.all(16),
                    decoration: glassDecoration(),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('Focus Level', style: TextStyle(fontWeight: FontWeight.bold)),
                        const SizedBox(height: 8),
                        Expanded(child: _buildChart(_focusData, Colors.green)),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                // Stress graph
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.all(16),
                    decoration: glassDecoration(),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('Stress Level', style: TextStyle(fontWeight: FontWeight.bold)),
                        const SizedBox(height: 8),
                        Expanded(child: _buildChart(_stressData, Colors.red)),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                // EEG bands
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: glassDecoration(),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      _bandBar('δ', _delta, Colors.purple),
                      _bandBar('θ', _theta, Colors.blue),
                      _bandBar('α', _alpha, Colors.green),
                      _bandBar('β', _beta, Colors.orange),
                      _bandBar('γ', _gamma, Colors.red),
                    ],
                  ),
                ),
                const SizedBox(height: 20),
                // Start/Stop button
                GestureDetector(
                  onTap: _running ? _stop : _start,
                  child: Container(
                    width: 80,
                    height: 80,
                    decoration: BoxDecoration(
                      gradient: _running ? null : AppTheme.accentGradient,
                      color: _running ? Colors.red.withOpacity(0.3) : null,
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: _running ? Colors.red : Colors.transparent,
                        width: 2,
                      ),
                    ),
                    child: Icon(
                      _running ? Icons.stop : Icons.play_arrow,
                      size: 40,
                      color: Colors.white,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildGauge(String label, double value, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: glassDecoration(),
      child: Column(
        children: [
          Text(label, style: const TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Text(
            '${(value * 100).toInt()}%',
            style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: color),
          ),
          const SizedBox(height: 8),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: value,
              backgroundColor: Colors.white.withOpacity(0.1),
              color: color,
              minHeight: 6,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildChart(List<FlSpot> data, Color color) {
    if (data.isEmpty) {
      return const Center(child: Text('Press play to start monitoring'));
    }

    return LineChart(
      LineChartData(
        gridData: FlGridData(
          show: true,
          drawVerticalLine: false,
          horizontalInterval: 25,
          getDrawingHorizontalLine: (_) => FlLine(
            color: Colors.white.withOpacity(0.1),
            strokeWidth: 1,
          ),
        ),
        titlesData: const FlTitlesData(show: false),
        borderData: FlBorderData(show: false),
        minX: 0,
        maxX: 59,
        minY: 0,
        maxY: 100,
        lineBarsData: [
          LineChartBarData(
            spots: data,
            isCurved: true,
            color: color,
            barWidth: 2,
            isStrokeCapRound: true,
            dotData: const FlDotData(show: false),
            belowBarData: BarAreaData(
              show: true,
              color: color.withOpacity(0.2),
            ),
          ),
        ],
      ),
    );
  }

  Widget _bandBar(String label, double value, Color color) {
    return Column(
      children: [
        Text(label, style: TextStyle(color: color, fontWeight: FontWeight.bold)),
        const SizedBox(height: 4),
        Container(
          width: 30,
          height: 60,
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Align(
            alignment: Alignment.bottomCenter,
            child: Container(
              width: 30,
              height: 60 * value,
              decoration: BoxDecoration(
                color: color,
                borderRadius: BorderRadius.circular(8),
              ),
            ),
          ),
        ),
      ],
    );
  }
}
