import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../config/theme.dart';

/// Line chart widget for attention/stress visualization
/// Shows historical data with gradient fill
class AttentionGraph extends StatelessWidget {
  final List<double> data;
  final Color lineColor;
  final String label;
  final double maxY;
  final bool showPercentage;
  
  const AttentionGraph({
    super.key,
    required this.data,
    required this.lineColor,
    required this.label,
    this.maxY = 1.0,
    this.showPercentage = true,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.cardBackground,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppTheme.cardBorder),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Label and current value
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                label,
                style: AppTheme.labelUppercase.copyWith(
                  color: lineColor,
                ),
              ),
              if (data.isNotEmpty)
                Text(
                  showPercentage 
                      ? '${(data.last * 100).toInt()}%'
                      : data.last.toStringAsFixed(2),
                  style: AppTheme.headingMedium.copyWith(
                    color: lineColor,
                  ),
                ),
            ],
          ),
          
          const SizedBox(height: 12),
          
          // Chart
          SizedBox(
            height: 100,
            child: data.isEmpty
                ? Center(
                    child: Text(
                      'No data yet',
                      style: AppTheme.bodySmall,
                    ),
                  )
                : LineChart(
                    LineChartData(
                      gridData: FlGridData(
                        show: true,
                        drawVerticalLine: false,
                        horizontalInterval: 0.25,
                        getDrawingHorizontalLine: (value) {
                          return FlLine(
                            color: Colors.white.withAlpha(10),
                            strokeWidth: 1,
                          );
                        },
                      ),
                      titlesData: const FlTitlesData(show: false),
                      borderData: FlBorderData(show: false),
                      minX: 0,
                      maxX: (data.length - 1).toDouble().clamp(1, 60),
                      minY: 0,
                      maxY: maxY,
                      lineBarsData: [
                        LineChartBarData(
                          spots: data.asMap().entries.map((e) {
                            return FlSpot(e.key.toDouble(), e.value);
                          }).toList(),
                          isCurved: true,
                          curveSmoothness: 0.3,
                          color: lineColor,
                          barWidth: 3,
                          isStrokeCapRound: true,
                          dotData: const FlDotData(show: false),
                          belowBarData: BarAreaData(
                            show: true,
                            gradient: LinearGradient(
                              begin: Alignment.topCenter,
                              end: Alignment.bottomCenter,
                              colors: [
                                lineColor.withAlpha(100),
                                lineColor.withAlpha(20),
                              ],
                            ),
                          ),
                        ),
                      ],
                      lineTouchData: LineTouchData(
                        enabled: true,
                        touchTooltipData: LineTouchTooltipData(
                          getTooltipColor: (_) => AppTheme.cardBackground,
                          getTooltipItems: (spots) {
                            return spots.map((spot) {
                              return LineTooltipItem(
                                showPercentage
                                    ? '${(spot.y * 100).toInt()}%'
                                    : spot.y.toStringAsFixed(2),
                                TextStyle(
                                  color: lineColor,
                                  fontWeight: FontWeight.bold,
                                ),
                              );
                            }).toList();
                          },
                        ),
                      ),
                    ),
                  ),
          ),
        ],
      ),
    );
  }
}

/// Compact band power bar chart
class BandPowerChart extends StatelessWidget {
  final Map<String, double> bandPowers;
  
  const BandPowerChart({
    super.key,
    required this.bandPowers,
  });
  
  static const Map<String, Color> bandColors = {
    'delta': Color(0xFF6366F1), // Indigo
    'theta': Color(0xFF8B5CF6), // Purple
    'alpha': Color(0xFF06B6D4), // Cyan
    'beta': Color(0xFF10B981),  // Green
    'gamma': Color(0xFFF59E0B), // Amber
  };

  @override
  Widget build(BuildContext context) {
    final bands = ['delta', 'theta', 'alpha', 'beta', 'gamma'];
    final maxPower = bandPowers.values.isEmpty 
        ? 50.0 
        : bandPowers.values.reduce((a, b) => a > b ? a : b).clamp(1.0, 100.0);
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.cardBackground,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppTheme.cardBorder),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'EEG BAND POWERS',
            style: AppTheme.labelUppercase,
          ),
          const SizedBox(height: 16),
          
          ...bands.map((band) {
            final power = bandPowers[band] ?? 0.0;
            final color = bandColors[band] ?? Colors.grey;
            
            return Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(
                children: [
                  SizedBox(
                    width: 48,
                    child: Text(
                      band[0].toUpperCase() + band.substring(1),
                      style: AppTheme.bodySmall.copyWith(
                        color: color,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  Expanded(
                    child: Container(
                      height: 12,
                      decoration: BoxDecoration(
                        color: Colors.white.withAlpha(10),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: FractionallySizedBox(
                        alignment: Alignment.centerLeft,
                        widthFactor: (power / maxPower).clamp(0.0, 1.0),
                        child: Container(
                          decoration: BoxDecoration(
                            color: color,
                            borderRadius: BorderRadius.circular(6),
                            boxShadow: [
                              BoxShadow(
                                color: color.withAlpha(100),
                                blurRadius: 8,
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  SizedBox(
                    width: 40,
                    child: Text(
                      power.toStringAsFixed(1),
                      style: AppTheme.bodySmall,
                      textAlign: TextAlign.right,
                    ),
                  ),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }
}
