import 'package:flutter_test/flutter_test.dart';
import 'package:neuro_mentor/main.dart';

void main() {
  testWidgets('App starts', (WidgetTester tester) async {
    await tester.pumpWidget(const NeuroMentorApp());
    expect(find.byType(NeuroMentorApp), findsOneWidget);
  });
}
