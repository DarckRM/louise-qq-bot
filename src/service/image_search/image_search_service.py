from typing import Callable, Dict, List, Tuple

from botpy.message import DirectMessage
from config.conf import CONF
from src.http.http_client import get_http_client
from src.model.enum import FeatureType
from src.service.servicer import Servicer
from botpy import logger


class SauceNAO(Servicer):

    def __init__(self) -> None:
        self.feature_map: Dict[str, Tuple[FeatureType, Callable]] = {}
        self.feature_map["find"] = (FeatureType.SYNC, self._saucenao)

        self.http_client = get_http_client()

    def name(self) -> str:
        return "saucenao"


    def get_feature(self, feature_name: str) -> (FeatureType, Callable):
        feature_type, feature = self.feature_map.get(feature_name, (None, None))
        if not feature:
            logger.warning(f"{self.name()} 服务不存在 {feature_name}")
            return None, None
        return feature_type, feature


    async def _saucenao(self, message: DirectMessage):
        img_url = "https://" + message.attachments[0].url
        logger.info(f"收到发送的消息: {message.content}")
        saucenao_result: Dict = await self.http_client.url(f"{CONF['saucenao.url']}?url={img_url}&api_key={CONF['saucenao.key']}&db=999&output_type=2&numres=5").get()

        header: Dict = saucenao_result["header"]
        results: List[Dict] = saucenao_result["results"]

        logger.info(saucenao_result)