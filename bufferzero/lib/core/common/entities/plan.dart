class Plan {
  final String id;
  final int maxRequests;
  final int? validityDays;
  final String maxVideoQuality;
  final String maxAudioQuality;
  final bool playlistSupport;
  final bool subtitleSupport;
  final bool audioOnlySupport;
  final bool audioLanguageSupport;
  final int priceInr;
  final List<String> audioQualities;
  final List<String> videoQualities;


  Plan({
    required this.id,
    required this.maxRequests,
    required this.validityDays,
    required this.maxVideoQuality,
    required this.maxAudioQuality,
    required this.playlistSupport,
    required this.subtitleSupport,
    required this.audioOnlySupport,
    required this.audioLanguageSupport,
    required this.priceInr,
    required this.audioQualities,
    required this.videoQualities,
  });
}