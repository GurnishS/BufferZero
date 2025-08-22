from enum import Enum

class AudioQuality(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    
    @classmethod
    def list(cls):
        return [quality.value for quality in cls]