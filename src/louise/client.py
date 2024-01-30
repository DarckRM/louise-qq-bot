from http import client
from typing import Any, Dict, List, Optional, Union
import botpy
from botpy.flags import Intents
from botpy.message import DirectMessage
from botpy import logger
from src.model.enum import FeatureType
from src.model.object import WaitingSession
from src.service.servicer import Servicer

from src.handler.direct_message import DirectMessageHandler

class LouiseClient(botpy.Client):
    
    def __init__(self, intents: Intents, timeout: int = 5, is_sandbox=False, log_config: str | dict = None, log_format: str = None, log_level: int = None, bot_log: bool | None = True, ext_handlers: dict | List[dict] | bool = True):
        super().__init__(intents, timeout, is_sandbox, log_config, log_format, log_level, bot_log, ext_handlers)
        
        self.servicer_map: Dict[str, Servicer] = {}

        self.direct_message_handler = DirectMessageHandler()

    
    def connect(self, conf: Dict, servicer_list: List[Servicer]):
        for s in servicer_list:
            self.servicer_map[s.name()] = s
            self.direct_message_handler.servicer_map[s.name()] = s

    async def on_direct_message_create(self, message: DirectMessage):
        content = message.content
        attachments = message.attachments
        if not content and not attachments:
            return

        await self.direct_message_handler.on_message(message)
        

client: LouiseClient = None

def get_louise_client(conf: Dict = None, servicer_list: List[Servicer] = [], intents: Intents = None, timeout: int = 5, is_sandbox=False, log_config: str | dict = None, log_format: str = None, log_level: int = None, bot_log: bool | None = True, ext_handlers: dict | List[dict] | bool = True) -> LouiseClient:
    global client
    if not client:
        client = LouiseClient(intents, timeout, is_sandbox, log_config, log_format, log_level, bot_log, ext_handlers)
        client.connect(conf, servicer_list)

    return client