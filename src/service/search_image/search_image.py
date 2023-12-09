import os
from typing import Any, Callable, Dict, List, Set, Tuple
from src.model.constant import CACHE_PATH_IMAGES
from src.http.http_client import HttpClient, get_http_client

from src.model.enum import FeatureType
from src.service.servicer import Servicer
from botpy import logger
from botpy.message import DirectMessage
from src.http.http_client import get_http_client

CACHE_YANDE: str = CACHE_PATH_IMAGES + "yande/"

class SearchImage(Servicer):

    def __init__(self) -> None:
        self.feature_map: Dict[str, Tuple[FeatureType, Callable]] = {}
        self.feature_map["find"] = (FeatureType.ASYNC, self._find)
        self.feature_map["yande"] = (FeatureType.SYNC, self._yande)

        self.http_client = get_http_client()
    
    
    def name(self) -> str:
        return "search_image"

    def get_feature(self, feature_name: str) -> (FeatureType, Callable):
        feature_type, feature = self.feature_map.get(feature_name, (None, None))
        if not feature:
            logger.warning(f"{self.name()} 服务不存在 {feature_name}")
            return None, None
        return feature_type, feature
    
    async def _find(self, message: DirectMessage):
        logger.info("调用了 find 功能")

    
    async def _yande(self, message: DirectMessage):
        logger.info("调用了 random_setu 功能")
        images: List[bytes] = []

        results = await self.http_client.url(f"https://yande.re/post/popular_recent.json?limit=5&page=1").get()
        for r in results:
            images.append(await self.http_client.url(r["jpeg_url"]).get_bytes())
            file_name = r['md5'] + ".jpg"
            
            if not os.path.exists(CACHE_YANDE):
                os.makedirs(CACHE_YANDE)
            
            with open(CACHE_YANDE + file_name, "wb+") as f:
                f.write(images[-1])
            
            if len(images) == 5:
                break
        
        for image in images:
            await message.reply(content="这是你搜索的图片", file_image=image)
        return