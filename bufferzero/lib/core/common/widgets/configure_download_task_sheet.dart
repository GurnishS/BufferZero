import 'package:flutter/material.dart';

/// Shows the "Configure before download" bottom sheet matching the provided
/// screenshots. Returns true when the user taps Download, otherwise null.
Future<T?> showConfigureDownloadTaskSheet<T>(BuildContext context) {
  return showModalBottomSheet<T>(
    context: context,
    isScrollControlled: true,
    backgroundColor: Colors.transparent,
    shape: const RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
    ),
    builder: (ctx) => const _ConfigureDownloadTaskSheet(),
  );
}

class _ConfigureDownloadTaskSheet extends StatefulWidget {
  const _ConfigureDownloadTaskSheet({Key? key}) : super(key: key);

  @override
  State<_ConfigureDownloadTaskSheet> createState() =>
      _ConfigureDownloadTaskSheetState();
}

enum _DownloadType { audio, video, playlist }

enum _FormatChoice { preset, custom }

class _ConfigureDownloadTaskSheetState
    extends State<_ConfigureDownloadTaskSheet> {
  _DownloadType _downloadType = _DownloadType.video;
  _FormatChoice _formatChoice = _FormatChoice.preset;
  bool _downloadSubtitles = false;
  bool _saveThumbnail = false;
  late Map<_DownloadType, String> _selectedQuality;

  @override
  void initState() {
    super.initState();
    _selectedQuality = {
      _DownloadType.video: '2160p',
      _DownloadType.audio: 'High',
      _DownloadType.playlist: '2160p',
    };
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final tt = Theme.of(context).textTheme;

    return SafeArea(
      bottom: false,
      child: DraggableScrollableSheet(
        expand: false,
        initialChildSize: 0.72,
        minChildSize: 0.38,
        maxChildSize: 0.95,
        builder: (context, controller) {
          return Container(
            decoration: BoxDecoration(
              color: cs.surface,
              borderRadius: const BorderRadius.vertical(
                top: Radius.circular(20),
              ),
            ),
            padding: EdgeInsets.only(
              left: 20,
              right: 20,
              top: 12,
              bottom: MediaQuery.of(context).viewInsets.bottom + 18,
            ),
            child: SingleChildScrollView(
              controller: controller,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // handle
                  Center(
                    child: Container(
                      width: 40,
                      height: 4,
                      margin: const EdgeInsets.only(top: 6, bottom: 8),
                      decoration: BoxDecoration(
                        color: cs.onSurface.withOpacity(0.08),
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                  ),

                  // small icon under handle
                  Center(
                    child: Icon(
                      Icons.checklist_rounded,
                      color: cs.onSurface.withOpacity(0.6),
                      size: 22,
                    ),
                  ),

                  const SizedBox(height: 8),

                  // Title
                  Center(
                    child: Text(
                      'Configure before download',
                      style: tt.titleLarge?.copyWith(fontSize: 22),
                      textAlign: TextAlign.center,
                    ),
                  ),

                  const SizedBox(height: 18),

                  // Download type label
                  Text(
                    'Download type',
                    style: tt.bodyMedium?.copyWith(
                      color: cs.primary.withOpacity(0.9),
                    ),
                  ),

                  const SizedBox(height: 10),

                  // Segmented control: Audio | Video | Playlist
                  Container(
                    padding: const EdgeInsets.all(2),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(32),
                      border: Border.all(color: cs.onSurface.withOpacity(0.12)),
                    ),
                    child: Row(
                      children: [
                        _buildSegment("Audio", _DownloadType.audio, cs),
                        _buildSegment("Video", _DownloadType.video, cs),
                        _buildSegment("Playlist", _DownloadType.playlist, cs),
                      ],
                    ),
                  ),

                  const SizedBox(height: 18),

                  Text(
                    'Format selection',
                    style: tt.bodyMedium?.copyWith(
                      color: cs.onSurface.withOpacity(0.9),
                    ),
                  ),

                  const SizedBox(height: 12),

                  // Preset card
                  GestureDetector(
                    onTap: () {
                      // if preset already selected, open quality selector
                      if (_formatChoice == _FormatChoice.preset) {
                        _showQualitySelector(context);
                        return;
                      }
                      setState(() => _formatChoice = _FormatChoice.preset);
                    },
                    child: Container(
                      width: double.infinity,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 18,
                      ),
                      decoration: BoxDecoration(
                        color: _formatChoice == _FormatChoice.preset
                            ? cs.primaryContainer
                            : cs.surfaceVariant,
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Row(
                        children: [
                          Icon(
                            Icons.settings,
                            color: _formatChoice == _FormatChoice.preset
                                ? cs.onPrimaryContainer
                                : cs.onSurface.withOpacity(0.9),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Preset',
                                  style: tt.titleMedium?.copyWith(
                                    color: _formatChoice == _FormatChoice.preset
                                        ? cs.onPrimaryContainer
                                        : cs.onSurface,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  'Prefer Quality, ${_selectedQuality[_downloadType]}',
                                  style: tt.bodySmall?.copyWith(
                                    color: _formatChoice == _FormatChoice.preset
                                        ? cs.onPrimaryContainer.withOpacity(0.9)
                                        : cs.onSurface.withOpacity(0.7),
                                  ),
                                ),
                              ],
                            ),
                          ),
                          Icon(
                            Icons.more_vert,
                            color: _formatChoice == _FormatChoice.preset
                                ? cs.onPrimaryContainer
                                : cs.onSurface.withOpacity(0.7),
                          ),
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 12),

                  // Custom card
                  GestureDetector(
                    onTap: () =>
                        setState(() => _formatChoice = _FormatChoice.custom),
                    child: Container(
                      width: double.infinity,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 18,
                      ),
                      decoration: BoxDecoration(
                        color: cs.surfaceVariant,
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: Row(
                        children: [
                          Icon(
                            Icons.description,
                            color: cs.onSurface.withOpacity(0.9),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Custom',
                                  style: tt.titleMedium?.copyWith(
                                    color: cs.onSurface,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  'Choose from formats, subtitles, and customize further',
                                  style: tt.bodySmall?.copyWith(
                                    color: cs.onSurface.withOpacity(0.7),
                                  ),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(width: 8),
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 18),

                  // Additional settings header
                  Text(
                    'Additional settings',
                    style: tt.bodyMedium?.copyWith(
                      color: cs.onSurface.withOpacity(0.9),
                    ),
                  ),
                  const SizedBox(height: 12),

                  Wrap(
                    spacing: 12,
                    runSpacing: 8,
                    children: [
                      _buildToggleChip(
                        'Download subtitles',
                        _downloadSubtitles,
                        (v) => setState(() => _downloadSubtitles = v),
                        cs,
                      ),
                      _buildToggleChip(
                        'Save thumbnail',
                        _saveThumbnail,
                        (v) => setState(() => _saveThumbnail = v),
                        cs,
                      ),
                    ],
                  ),

                  const SizedBox(height: 20),

                  // Buttons row
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: () => Navigator.of(context).pop(),
                          icon: Icon(
                            Icons.close,
                            color: cs.onSurface.withOpacity(0.9),
                          ),
                          label: Text(
                            'Cancel',
                            style: TextStyle(
                              color: cs.onSurface.withOpacity(0.9),
                            ),
                          ),
                          style: OutlinedButton.styleFrom(
                            side: BorderSide(
                              color: cs.onSurface.withOpacity(0.12),
                            ),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(30),
                            ),
                            padding: const EdgeInsets.symmetric(vertical: 14),
                            backgroundColor: Colors.transparent,
                          ),
                        ),
                      ),
                      const SizedBox(width: 14),
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: () => Navigator.of(context).pop(true),
                          icon: Icon(Icons.download, color: cs.onPrimary),
                          label: Text(
                            'Download',
                            style: TextStyle(color: cs.onPrimary),
                          ),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: cs.primary,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(30),
                            ),
                            padding: const EdgeInsets.symmetric(vertical: 14),
                          ),
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 8),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildSegment(String label, _DownloadType type, ColorScheme cs) {
    final bool selected = _downloadType == type;
    return Expanded(
      child: GestureDetector(
        onTap: () => setState(() => _downloadType = type),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            color: selected ? cs.primaryContainer : Colors.transparent,
            borderRadius: BorderRadius.circular(28),
          ),
          child: Center(
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                if (selected) ...[
                  Icon(Icons.check, size: 16, color: cs.onPrimaryContainer),
                  const SizedBox(width: 8),
                ],
                Text(
                  label,
                  style: TextStyle(
                    color: selected ? cs.onPrimaryContainer : cs.onSurface,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildToggleChip(
    String label,
    bool value,
    ValueChanged<bool> onChanged,
    ColorScheme cs,
  ) {
    return GestureDetector(
      onTap: () => onChanged(!value),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          color: value ? cs.primaryContainer : cs.surfaceVariant,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Text(
          label,
          style: TextStyle(color: value ? cs.onPrimaryContainer : cs.onSurface),
        ),
      ),
    );
  }

  Future<void> _showQualitySelector(BuildContext context) async {
    final cs = Theme.of(context).colorScheme;
    final tt = Theme.of(context).textTheme;

    final isAudio = _downloadType == _DownloadType.audio;
    final options = isAudio
        ? ['Low', 'Medium', 'High']
        : ['144p', '240p', '360p', '480p', '720p', '1080p', '1440p', '2160p'];

    String current = _selectedQuality[_downloadType]!;

    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return StatefulBuilder(
          builder: (ctx, setStateModal) {
            return SafeArea(
              bottom: false,
              child: Container(
                decoration: BoxDecoration(
                  color: cs.surface,
                  borderRadius: const BorderRadius.vertical(
                    top: Radius.circular(20),
                  ),
                ),
                padding: EdgeInsets.only(
                  left: 20,
                  right: 20,
                  top: 12,
                  bottom: MediaQuery.of(context).viewInsets.bottom + 18,
                ),
                child: SingleChildScrollView(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Center(
                        child: Container(
                          width: 40,
                          height: 4,
                          margin: const EdgeInsets.only(top: 6, bottom: 8),
                          decoration: BoxDecoration(
                            color: cs.onSurface.withOpacity(0.08),
                            borderRadius: BorderRadius.circular(2),
                          ),
                        ),
                      ),
                      const SizedBox(height: 6),
                      Center(
                        child: Text(
                          isAudio
                              ? 'Preferred audio quality'
                              : 'Preferred video quality',
                          style: tt.titleLarge?.copyWith(fontSize: 20),
                        ),
                      ),
                      const SizedBox(height: 16),
                      for (final opt in options)
                        RadioListTile<String>(
                          title: Text(opt),
                          value: opt,
                          groupValue: current,
                          onChanged: (v) =>
                              setStateModal(() => current = v ?? current),
                        ),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          Expanded(
                            child: OutlinedButton(
                              onPressed: () => Navigator.of(ctx).pop(),
                              style: OutlinedButton.styleFrom(
                                side: BorderSide(
                                  color: cs.onSurface.withOpacity(0.12),
                                ),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(30),
                                ),
                                padding: const EdgeInsets.symmetric(
                                  vertical: 14,
                                ),
                              ),
                              child: Text(
                                'Cancel',
                                style: TextStyle(color: cs.onSurface),
                              ),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: ElevatedButton(
                              onPressed: () {
                                setState(
                                  () =>
                                      _selectedQuality[_downloadType] = current,
                                );
                                Navigator.of(ctx).pop();
                              },
                              style: ElevatedButton.styleFrom(
                                backgroundColor: cs.primary,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(30),
                                ),
                                padding: const EdgeInsets.symmetric(
                                  vertical: 14,
                                ),
                              ),
                              child: Text(
                                'Save',
                                style: TextStyle(color: cs.onPrimary),
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                    ],
                  ),
                ),
              ),
            );
          },
        );
      },
    );
  }
}
