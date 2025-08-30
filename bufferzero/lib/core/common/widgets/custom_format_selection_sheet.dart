import 'package:flutter/material.dart';

enum DownloadType { audio, video, playlist }

class FormatEntry {
  final String id;
  final String title;
  final String subtitle; // size + bitrate
  final String formatLine; // codec info
  final bool audioOnly;

  FormatEntry({
    required this.id,
    required this.title,
    required this.subtitle,
    required this.formatLine,
    this.audioOnly = false,
  });
}

/// Shows the full-screen format selection sheet.
/// Returns a map with keys 'video' and 'audio' containing selected ids (or null).
Future<Map<String, String?>?> showCustomFormatSelectionSheet(
  BuildContext context, {
  required DownloadType downloadType,
}) {
  return showModalBottomSheet<Map<String, String?>?>(
    context: context,
    isScrollControlled: true,
    backgroundColor: Colors.transparent,
    builder: (ctx) => _CustomFormatSelectionSheet(downloadType: downloadType),
  );
}

class _CustomFormatSelectionSheet extends StatefulWidget {
  final DownloadType downloadType;

  const _CustomFormatSelectionSheet({Key? key, required this.downloadType})
    : super(key: key);

  @override
  State<_CustomFormatSelectionSheet> createState() =>
      _CustomFormatSelectionSheetState();
}

class _CustomFormatSelectionSheetState
    extends State<_CustomFormatSelectionSheet> {
  bool _loading = true;
  late List<FormatEntry> _audioFormats;
  late List<FormatEntry> _videoNoAudioFormats;
  late List<FormatEntry> _videoWithAudioFormats;
  String? _selectedAudioId;
  String? _selectedVideoId;
  bool _selectedVideoHasAudio = false;

  @override
  void initState() {
    super.initState();
    // Simulate network call
    Future.delayed(const Duration(milliseconds: 800), _loadSampleData);
  }

  void _loadSampleData() {
    _audioFormats = [
      FormatEntry(
        id: 'audio_251',
        title: '251 - audio only (medium)',
        subtitle: '18.01 MB 134.0 Kbps',
        formatLine: 'WEBM (NONE OPUS)',
        audioOnly: true,
      ),
      FormatEntry(
        id: 'audio_140',
        title: '140 - audio only (medium)',
        subtitle: '17.39 MB 129.5 Kbps',
        formatLine: 'M4A (NONE MP4A)',
        audioOnly: true,
      ),
      FormatEntry(
        id: 'audio_250',
        title: '250 - audio only (low)',
        subtitle: '9.75 MB 72.6 Kbps',
        formatLine: 'WEBM (NONE OPUS)',
        audioOnly: true,
      ),
      FormatEntry(
        id: 'audio_249',
        title: '249 - audio only (low)',
        subtitle: '7.13 MB 53.1 Kbps',
        formatLine: 'WEBM (NONE OPUS)',
        audioOnly: true,
      ),
    ];

    // Split video formats into two lists: some formats include audio, others are
    // video-only (no audio). This allows selecting audio + video(no-audio),
    // while preventing selecting audio together with a video that already
    // contains audio.
    _videoNoAudioFormats = [
      FormatEntry(
        id: 'v_248',
        title: '248 - 1920x1080 (1080p)',
        subtitle: '123.47 MB 919.1 Kbps',
        formatLine: 'WEBM (VP9 NONE)',
      ),
      FormatEntry(
        id: 'v_247',
        title: '247 - 1280x720 (720p)',
        subtitle: '67.33 MB 501.2 Kbps',
        formatLine: 'WEBM (VP9 NONE)',
      ),
      FormatEntry(
        id: 'v_398',
        title: '398 - 1280x720 (720p)',
        subtitle: '56.90 MB 423.5 Kbps',
        formatLine: 'MP4 (AV01 NONE)',
      ),
    ];

    _videoWithAudioFormats = [
      FormatEntry(
        id: 'v_137',
        title: '137 - 1920x1080 (1080p) - with audio',
        subtitle: '184.66 MB 1.34 Mbps',
        formatLine: 'MP4 (AVC1 NONE)',
      ),
      FormatEntry(
        id: 'v_399',
        title: '399 - 1920x1080 (1080p) - with audio',
        subtitle: '102.74 MB 764.8 Kbps',
        formatLine: 'MP4 (AV01 NONE)',
      ),
      FormatEntry(
        id: 'v_18',
        title: '18 - 640x360 (360p) - with audio',
        subtitle: '59.41 MB 442.2 Kbps',
        formatLine: 'MP4 (AVC1 MP4A)',
      ),
    ];

    setState(() => _loading = false);
  }

  bool get _isAudioOnly => widget.downloadType == DownloadType.audio;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final tt = Theme.of(context).textTheme;

    return SafeArea(
      bottom: false,
      child: SizedBox(
        height: MediaQuery.of(context).size.height * 0.95,
        child: Container(
          decoration: BoxDecoration(
            color: cs.surface,
            borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
          ),
          child: _loading
              ? Center(
                  child: SizedBox(
                    width: 56,
                    height: 56,
                    child: CircularProgressIndicator(color: cs.primary),
                  ),
                )
              : Column(
                  children: [
                    // AppBar row
                    Padding(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 12,
                      ),
                      child: Row(
                        children: [
                          IconButton(
                            onPressed: () => Navigator.of(context).pop(),
                            icon: Icon(Icons.close, color: cs.onSurface),
                          ),
                          Expanded(
                            child: Text(
                              'Format selection',
                              style: tt.titleLarge,
                            ),
                          ),
                        ],
                      ),
                    ),

                    Expanded(
                      child: SingleChildScrollView(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 8,
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            // Thumbnail and video info
                            Row(
                              children: [
                                Container(
                                  width: 100,
                                  height: 56,
                                  decoration: BoxDecoration(
                                    color: cs.surfaceVariant,
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: const Icon(Icons.image, size: 36),
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        'Why India\'s Censor Board is a Joke',
                                        style: tt.bodyLarge,
                                      ),
                                      const SizedBox(height: 4),
                                      Text(
                                        'Mohak Mangal',
                                        style: tt.bodySmall?.copyWith(
                                          color: cs.onSurface.withOpacity(0.7),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                IconButton(
                                  onPressed: () {},
                                  icon: Icon(
                                    Icons.more_vert,
                                    color: cs.onSurface.withOpacity(0.7),
                                  ),
                                ),
                              ],
                            ),

                            const SizedBox(height: 12),

                            // Subtitle languages
                            Wrap(
                              spacing: 8,
                              children: [
                                Chip(
                                  label: Text(
                                    'English (India)',
                                    style: TextStyle(color: cs.onPrimary),
                                  ),
                                  backgroundColor: cs.primaryContainer,
                                ),
                                TextButton(
                                  onPressed: () {},
                                  child: const Text('See all'),
                                ),
                              ],
                            ),

                            const SizedBox(height: 12),

                            // Suggested
                            Text('Suggested', style: tt.bodyMedium),
                            const SizedBox(height: 8),
                            _buildSuggestedCard(cs, tt),

                            const SizedBox(height: 12),

                            if (!_isAudioOnly) ...[
                              Text('Audio', style: tt.bodyMedium),
                              const SizedBox(height: 8),
                              _buildGrid(
                                _audioFormats,
                                isAudio: true,
                                cs: cs,
                                tt: tt,
                              ),
                              const SizedBox(height: 12),

                              // Video (no audio) section header
                              Text('Video (no audio)', style: tt.bodyMedium),
                              const SizedBox(height: 8),
                              _buildGrid(
                                _videoNoAudioFormats,
                                isAudio: false,
                                cs: cs,
                                tt: tt,
                                videoHasAudio: false,
                              ),
                              const SizedBox(height: 12),

                              // Video (with audio) section header
                              Text('Video (with audio)', style: tt.bodyMedium),
                              const SizedBox(height: 8),
                              _buildGrid(
                                _videoWithAudioFormats,
                                isAudio: false,
                                cs: cs,
                                tt: tt,
                                videoHasAudio: true,
                              ),

                              const SizedBox(height: 12),

                              // Info paragraph with icon (matches screenshots)
                              Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Icon(
                                    Icons.info_outline,
                                    color: cs.onSurface.withOpacity(0.7),
                                  ),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      'Most video streaming platforms deliver audio and video separately, you can select and merge an audio-only format with a video-only format to a single video.',
                                      style: tt.bodySmall?.copyWith(
                                        color: cs.onSurface.withOpacity(0.7),
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ] else ...[
                              // audio-only flows
                              Text('Audio', style: tt.bodyMedium),
                              const SizedBox(height: 8),
                              _buildGrid(
                                _audioFormats,
                                isAudio: true,
                                cs: cs,
                                tt: tt,
                              ),
                            ],

                            const SizedBox(height: 32),
                          ],
                        ),
                      ),
                    ),

                    // Bottom actions
                    Padding(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 12,
                      ),
                      child: Row(
                        children: [
                          Expanded(
                            child: OutlinedButton(
                              onPressed: () => Navigator.of(context).pop(),
                              style: OutlinedButton.styleFrom(
                                side: BorderSide(
                                  color: cs.onSurface.withOpacity(0.12),
                                ),
                                padding: const EdgeInsets.symmetric(
                                  vertical: 14,
                                ),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(30),
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
                            child: ElevatedButton.icon(
                              onPressed: () {
                                Navigator.of(context).pop({
                                  'video': _selectedVideoId,
                                  'audio': _selectedAudioId,
                                });
                              },
                              icon: Icon(Icons.download, color: cs.onPrimary),
                              label: Text(
                                'Select',
                                style: TextStyle(color: cs.onPrimary),
                              ),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: cs.primary,
                                padding: const EdgeInsets.symmetric(
                                  vertical: 14,
                                ),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(30),
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
        ),
      ),
    );
  }

  Widget _buildSuggestedCard(ColorScheme cs, TextTheme tt) {
    final suggestedText =
        '248 - 1920x1080 (1080p) + 251 - audio only (medium)\n141.47 MB 1.03 Mbps\nWEBM (VP9 OPUS)';
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: cs.surfaceVariant,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(suggestedText, style: tt.bodyMedium),
    );
  }

  Widget _buildGrid(
    List<FormatEntry> items, {
    required bool isAudio,
    required ColorScheme cs,
    required TextTheme tt,
    bool videoHasAudio = false,
  }) {
    return GridView.builder(
      physics: const NeverScrollableScrollPhysics(),
      shrinkWrap: true,
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        childAspectRatio: 2.4,
        crossAxisSpacing: 10,
        mainAxisSpacing: 10,
      ),
      itemCount: items.length,
      itemBuilder: (context, index) {
        final it = items[index];
        final bool selected = isAudio
            ? _selectedAudioId == it.id
            : _selectedVideoId == it.id;
        return GestureDetector(
          onTap: () {
            setState(() {
              if (isAudio) {
                // If a video that includes audio is currently selected, selecting
                // an audio format should first clear that video selection so the
                // audio can be chosen. This enforces "video-with-audio" and
                // "audio" not being selected together.
                if (_selectedVideoId != null && _selectedVideoHasAudio) {
                  _selectedVideoId = null;
                  _selectedVideoHasAudio = false;
                }

                _selectedAudioId = (_selectedAudioId == it.id) ? null : it.id;
              } else {
                // Selecting a video is single-select across both video lists.
                // videoHasAudio tells us whether this video already contains
                // audio. If it does, clear any audio selection.
                if (_selectedVideoId == it.id) {
                  _selectedVideoId = null;
                  _selectedVideoHasAudio = false;
                } else {
                  _selectedVideoId = it.id;
                  _selectedVideoHasAudio = videoHasAudio;
                }

                if (_selectedVideoHasAudio) {
                  // Clear audio selection when a video-with-audio is chosen.
                  _selectedAudioId = null;
                }
              }
            });
          },
          child: Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: selected ? cs.primaryContainer : cs.surfaceVariant,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: cs.onSurface.withOpacity(0.08)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  it.title,
                  style: tt.bodyMedium?.copyWith(
                    color: selected ? cs.onPrimaryContainer : cs.onSurface,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  it.subtitle,
                  style: tt.bodySmall?.copyWith(
                    color: selected
                        ? cs.onPrimaryContainer.withOpacity(0.9)
                        : cs.onSurface.withOpacity(0.7),
                  ),
                ),
                const SizedBox(height: 6),
                Expanded(
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Expanded(
                        child: Text(
                          it.formatLine,
                          style: tt.bodySmall?.copyWith(
                            color: selected
                                ? cs.onPrimaryContainer
                                : cs.onSurface.withOpacity(0.7),
                          ),
                        ),
                      ),
                      const SizedBox(width: 6),
                      Icon(
                        isAudio ? Icons.audiotrack : Icons.videocam,
                        size: 16,
                        color: selected
                            ? cs.onPrimaryContainer
                            : cs.onSurface.withOpacity(0.7),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
