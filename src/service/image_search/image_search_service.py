from typing import Any, Callable, Dict, List, Tuple

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
        logger.info(f"收到的图片: {img_url}")
        saucenao_result: Dict = await self.http_client.url(f"{CONF['saucenao.url']}?url={img_url}&api_key={CONF['saucenao.key']}&db=999&output_type=2&numres=5").get()

        header: Dict = saucenao_result["header"]
        results: List[Dict] = saucenao_result["results"]

        for r in results:
            content, image = self._resolve_saucenao_result(r)
            await message.reply(content=content, image=image)
    

    def _resolve_saucenao_result(self, result: Dict):
        header = result["header"]
        data = result["data"]

        similarity = float(header["similarity"])

        if similarity < 65:
            content, image = self._low_similarity_result(data, header)
        else:
            content, image = self._high_similarity_result(data, header)
        
        return content, image

    

    def _low_similarity_result(self, data: Dict, header: Dict) -> (str, Any):
        content = f"可能性较低的结果, 相似度 {header['similarity']}\n"
        image = header["thumbnail"]
        return content, image

    
    def _high_similarity_result(self, data: Dict, header: Dict) -> (str, Any):
        content = f"相似度 {header['similarity']}\n标题 {data['title']}\n"

        self._handle_different_source_result(int(header["index_id"]), data)
        
        image = header["thumbnail"]
        return content, image
    

    def _handle_different_source_result(self, index_id: int, data: Dict):
        match index_id:
            case 5:
                self._from_pixiv()
            case 4:
                self._from_twitter()
            case 12:
                self._from_yande(data)
            case (9, 25):
                self._from_gelbooru()
            case _:
                pass

    
    def _from_pixiv(self):
        pass


    def _from_twitter(self):
        pass


    def _from_yande(self, data: Dict) -> (str):
        post_id = data["yandere_id"]
        return "来源 Yande"

    def _from_gelbooru(self):
        pass