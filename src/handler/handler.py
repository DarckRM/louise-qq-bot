from typing import Dict
from model.object import WaitingSession


def add_waiting_session(session_map: Dict[str, WaitingSession], session: WaitingSession):
   session_map