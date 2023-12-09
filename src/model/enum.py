from enum import Enum

class FeatureType(Enum):
    SYNC: int = 0
    ASYNC: int = 1

class MessageType(Enum):
    SYNC: int = 0
    ASYNC: int = 1