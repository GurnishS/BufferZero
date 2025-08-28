class UserPrefs {
  final VideoQuality videoQuality;
  final AudioQuality audioQuality;
  final bool downloadSubtitles;
  final bool audioOnly;
  final bool isPlaylist;

  UserPrefs({
    required this.videoQuality,
    required this.audioQuality,
    required this.downloadSubtitles,
    required this.audioOnly,
    required this.isPlaylist,
  });
}

enum VideoQuality {
  p144("p144"),
  p240("p240"),
  p360("p360"),
  p480("p480"),
  p720("p720"),
  p1080("p1080"),
  p1440("p1440"),
  p2160("p2160");

  final String label;
  const VideoQuality(this.label);

  @override
  String toString() => label;

  static VideoQuality fromString(String value) =>
      VideoQuality.values.firstWhere((e) => e.label == value);
}

enum AudioQuality {
  low("low"),
  medium("medium"),
  high("high");

  final String label;
  const AudioQuality(this.label);

  @override
  String toString() => label;

  static AudioQuality fromString(String value) =>
      AudioQuality.values.firstWhere((e) => e.label == value);
}
