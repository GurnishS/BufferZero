import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class FloatingDownloadButton extends StatefulWidget {
  const FloatingDownloadButton({super.key});

  @override
  State<FloatingDownloadButton> createState() => _FloatingDownloadButtonState();
}

class _FloatingDownloadButtonState extends State<FloatingDownloadButton> {
  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return FloatingActionButton(
      onPressed: () => context.push('/downloads'),
      backgroundColor: colorScheme.primary,
      foregroundColor: colorScheme.onPrimary,
      elevation: 6,
      child: const Icon(Icons.download, size: 28),
    );
  }
}
