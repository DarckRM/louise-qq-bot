from attr import dataclass

@dataclass
class WaitingSession():
    user_id: str = None
    guild_id: str = None
    message_id: str = None
    handler: str = None
    service: str = None
    feature: str = None