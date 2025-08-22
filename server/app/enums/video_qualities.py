from enum import Enum

class VideoQuality(Enum):
    p144 = "144p"
    p240 = "240p"
    p360 = "360p"
    p480 = "480p"
    p720 = "720p"
    p1080 = "1080p"
    p1440 = "1440p"
    p2160 = "2160p"
    Premium = "Premium"

    @classmethod
    def list(cls):
        return [quality.value for quality in cls]