from multiprocessing.dummy import Pool
import time
import traceback
from typing import Dict
from botpy.message import DirectMessage
from src.handler.waitting_session import get_session, pop_session
from src.service.servicer import Servicer
from botpy import logger

class DirectMessageHandler():
    def __init__(self) -> None:
        self.name = "direct_message_handler"
        self.servicer_map: Dict[str, Servicer] = {}

        self.pool = Pool(6)

    
    async def on_command(self, message: DirectMessage):
        user = message.author


    async def on_message(self, message: DirectMessage):
        user = message.author

        for name, servicer in self.servicer_map.items():
            result = await servicer.invoke(message)
            if result >= 0:
                logger.info(f"调用 {name}")
                break

        session = get_session(user.id)
        if not session:
            return
        
        servicer = self.servicer_map.get(session.service, None)

        _, feature = servicer.get_feature(session.feature)
        try:
            await feature(message)
        except Exception as e:
            logger.error(f"执行功能异常: {e}\n{traceback.format_exc()}")
        pop_session(user.id)


    def _handle_message(self):
        while True:
            time.sleep(1)