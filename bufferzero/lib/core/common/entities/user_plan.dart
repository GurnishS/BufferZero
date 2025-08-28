class UserPlan {
  final String id;
  final String userId;
  final String planId;
  final DateTime createdAt;
  final DateTime validTill;
  final int maxRequests;
  final int requestsMade;
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


  UserPlan({
    required this.id,
    required this.userId,
    required this.planId,
    required this.createdAt,
    required this.validTill,
    required this.maxRequests,
    required this.requestsMade,
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
