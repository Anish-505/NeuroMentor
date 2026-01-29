import 'dart:convert';
import 'dart:math';
import 'package:http/http.dart' as http;
import '../config/technical_articles.dart';

/// Service for fetching Wikipedia article summaries
class WikipediaService {
  static const String _baseUrl = 'https://en.wikipedia.org/api/rest_v1/page/summary';
  
  static final List<String> _technicalTopics = [
    'Neural_network',
    'Machine_learning',
    'Electroencephalography',
    'Brain-computer_interface',
    'Neuroscience',
    'Cognitive_psychology',
    'Attention',
    'Memory',
    'Neuroplasticity',
    'Deep_learning',
    'Artificial_intelligence',
    'Signal_processing',
    'Fourier_transform',
    'Microcontroller',
    'Embedded_system',
  ];
  
  /// Fetch a random technical article from Wikipedia
  /// Falls back to local articles if request fails
  static Future<Article> fetchRandomArticle({int timeoutSec = 5}) async {
    final random = Random();
    final topic = _technicalTopics[random.nextInt(_technicalTopics.length)];
    
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/$topic'),
        headers: {'Accept': 'application/json'},
      ).timeout(Duration(seconds: timeoutSec));
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final title = data['title'] as String? ?? topic;
        final extract = data['extract'] as String? ?? '';
        
        if (extract.isNotEmpty) {
          return Article(
            title: '$title (Wikipedia)',
            content: _cleanText(extract),
          );
        }
      }
    } catch (e) {
      // Fall through to local article
    }
    
    // Fallback to local article
    final localArticle = localArticles[random.nextInt(localArticles.length)];
    return Article(
      title: '${localArticle.title} (Local)',
      content: localArticle.content,
    );
  }
  
  /// Clean up Wikipedia text
  static String _cleanText(String text) {
    // Remove parenthetical pronunciations and clean up whitespace
    return text
        .replaceAll(RegExp(r'\s*\([^)]*pronunciation[^)]*\)'), '')
        .replaceAll(RegExp(r'\s+'), ' ')
        .trim();
  }
}
