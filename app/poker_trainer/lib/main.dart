import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

const pokerBackground = Color(0xFF030F0B);

void main() {
  WidgetsFlutterBinding.ensureInitialized();

  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.light,
      statusBarBrightness: Brightness.dark,
      systemNavigationBarColor: pokerBackground,
      systemNavigationBarIconBrightness: Brightness.light,
    ),
  );

  runApp(const PokerApp());
}

class PokerApp extends StatelessWidget {
  const PokerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Poker UI',
      theme: ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: pokerBackground,
      ),
      home: const PokerScreen(),
    );
  }
}

class PokerScreen extends StatelessWidget {
  const PokerScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const AnnotatedRegion<SystemUiOverlayStyle>(
      value: SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: Brightness.light,
        statusBarBrightness: Brightness.dark,
        systemNavigationBarColor: pokerBackground,
        systemNavigationBarIconBrightness: Brightness.light,
      ),
      child: Scaffold(
        backgroundColor: pokerBackground,
        body: SizedBox.expand(),
      ),
    );
  }
}