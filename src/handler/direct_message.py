from multiprocessing.dummy import Pool
import time
import traceback
from typing import Dict, List
from botpy.message import DirectMessage
from src.service.servicer import Servicer
from botpy import logger
from src.model.object import WaitingSession

class DirectMessageHandler():
    def __init__(self) -> None:
        self.name = "direct_message_handler"
        self.waiting_session: Dict[str, WaitingSession] = {}
        self.servicer_map: Dict[str, Servicer] = {}

        self.pool = Pool(6)

    
    async def on_command(self, message: DirectMessage):
        user = message.author


    async def on_message(self, message: DirectMessage):
        user = message.author

        session = self.waiting_session.get(user.id, None)
        if not session:
            return
        
        servicer = self.servicer_map.get(session.service, None)
        if not servicer:
            return

        _, feature = servicer.get_feature(session.feature)
        try:
            await feature(message)
        except Exception as e:
            logger.error(f"执行功能异常: {e}\n{traceback.format_exc()}")
        self.waiting_session.pop(user.id)


    def _handle_message(self):
        while True:
            time.sleep(1)