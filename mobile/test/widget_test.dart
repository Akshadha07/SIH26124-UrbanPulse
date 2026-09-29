import 'package:flutter_test/flutter_test.dart';
import 'package:bel_urbanpulse_citizen/main.dart';

void main() {
  testWidgets('UrbanPulse app loads', (WidgetTester tester) async {
    await tester.pumpWidget(const UrbanPulseApp());

    expect(find.byType(UrbanPulseApp), findsOneWidget);
    expect(find.byType(MainNavigationShell), findsOneWidget);
  });
}