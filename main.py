from typing import List
import botpy
from config.conf import CONF
from src.http.http_client import get_http_client
from src.service.search_image.search_image import SearchImage
from src.service.servicer import Servicer

from src.louise.client import get_louise_client
from src.utils.logger import DEFAULT_FILE_HANDLER, DEFAULT_PRINT_FORMAT

http_client = get_http_client(CONF["proxy"])

intends = botpy.Intents(direct_message=True)
servicer_list: List[Servicer] = [
    SearchImage()
]

client = get_louise_client(conf=None, servicer_list=servicer_list, intents=intends, log_format=DEFAULT_PRINT_FORMAT, ext_handlers=DEFAULT_FILE_HANDLER)

client.run(appid=CONF["appid"], token=CONF["token"])