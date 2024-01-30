from typing import Dict, Optional

from botpy import user

from src.model.object import WaitingSession

waiting_session: Dict[str, WaitingSession] = {}

def add_session(user_id: str, session: WaitingSession):
    waiting_session[user_id] = session

def get_session(user_id: str) -> Optional[WaitingSession]:
    session = waiting_session.get(user_id)
    return session

def pop_session(user_id: str) -> bool:
    if waiting_session.pop(user_id):
        return True
    return False