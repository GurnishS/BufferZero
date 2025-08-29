import 'package:bufferzero/core/common/widgets/bottom_download_sheet.dart';
import 'package:flutter/material.dart';

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
      onPressed: () => {BottomDownloadSheet.show(context)},
      backgroundColor: colorScheme.primary,
      foregroundColor: colorScheme.onPrimary,
      elevation: 6,
      child: const Icon(Icons.download, size: 28),
    );
  }
}
