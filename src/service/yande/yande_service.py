import os
import traceback
from typing import Any, Callable, Dict, List, Set, Tuple
from src.model.db_model import LouiseBooruImage
from src.db.mysql.database import LousieDatabase, get_database
from src.model.constant import CACHE_PATH_IMAGES
from src.http.http_client import get_http_client

from src.model.enum import FeatureType
from src.service.servicer import Servicer
from botpy import logger
from botpy.message import DirectMessage

CACHE_YANDE: str = CACHE_PATH_IMAGES + "yande/"

db: LousieDatabase = get_database()

class BooruImage(Servicer):

    def __init__(self) -> None:
        self.feature_map: Dict[str, Tuple[FeatureType, Callable]] = {}
        self.feature_map["yande"] = (FeatureType.SYNC, self._yande)

        self.http_client = get_http_client()
    
    
    def name(self) -> str:
        return "booru_images"


    def get_feature(self, feature_name: str) -> (FeatureType, Callable):
        feature_type, feature = self.feature_map.get(feature_name, (None, None))
        if not feature:
            logger.warning(f"{self.name()} 服务不存在 {feature_name}")
            return None, None
        return feature_type, feature
    

    async def _yande(self, message: DirectMessage):
        logger.info("调用了 random_setu 功能")
        images: List[bytes] = []

        content = message.content.strip()
        if "/" in content:
            url = f"https://yande.re/post/popular_by_{content.split('/')[1]}.json?"
        else:
            url = "https://yande.re/post.json?"

        page_nation: List[int] = [5, 1]        
        cn_names: List[str] = []
        page_index = 0
        content_array: List[str] = content.split(' ')

        content_array.pop(0)
        for word in content_array:
            if word.isdigit():
                if page_index > 1:
                    continue
                page_nation[page_index] = (int(word))
                page_index += 1
            else:
                cn_names.append(word)

        images = await self._search_yande_image(url, cn_names, page_nation[0], page_nation[1])

        if not images:
            await message.reply(content="由于图片过大或某些意外无法发送图片哦")
            return
        
        for image in images:
            sample = f"作者: {image['author']}\n标签: {image['tags']}"
            try:
                await message.reply(content=sample, file_image=image["image"])
            except Exception as e:
                logger.error(f"发送消息失败: {e}\n{traceback.format_exc()}")
        
        await message.reply(content=f"你的请求参数 {cn_names}, 本次共返回 {len(images)} 张图片")

            
    async def _search_yande_image(self, url: str, cn_names: List[str], limit: int = 5, page: int = 1) -> List[Dict]:
        tags: str = ""
        images: List[Dict] = []
        louise_images: List[LouiseBooruImage] = []

        for cn_name in cn_names:
            tag = db.get_booru_tag(cn_name)
            if not tag:
                continue
            tags += tag.origin_name + '+'
        if len(tags) == 0:
            tags = '*+'
        url = f"{url}tags={tags[:-1]}&limit={limit}&page={page}"
        logger.info(f"请求: {url}")

        results = await self.http_client.url(url).get()
        count = 0
        for r in results:
            if count == 10:
                break
            count += 1
            louise_images.append(self._build_booru_image(r))
            try:
                images.append({
                    "author": r["author"],
                    "tags": r["tags"],
                    "url": r["file_url"][8:],
                    "source": r["source"][8:],
                    "image": await self._handle_yande_result(r)
                })
            except Exception as e:
                logger.error(f"处理 Yande 功能异常: {e}\n{traceback.format_exc()}")

        db.save_booru_image(louise_images)
        return images

    
    async def _handle_yande_result(self, r: Dict):
        image: bytes
        file_name = r['md5'] + ".jpg"
        if os.path.exists(CACHE_YANDE + file_name):
            with open(CACHE_YANDE + file_name, "rb+") as f:
                image = f.read()
        else:
            image = await self.http_client.url(r["jpeg_url"]).get_bytes()
        
        if not os.path.exists(CACHE_YANDE):
            os.makedirs(CACHE_YANDE)
        
        with open(CACHE_YANDE + file_name, "wb+") as f:
            f.write(image)
        
        return image
        
        
    def _build_booru_image(self, r: Dict) -> LouiseBooruImage:
        image: LouiseBooruImage = LouiseBooruImage(
            id=r["id"],
            tags=r["tags"],
            recorded_at=0,
            created_at=r["created_at"],
            updated_at=r["updated_at"],
            creator_id=r["creator_id"],
            author=r["author"],
            source=r["source"],
            md5=r["md5"],
            file_ext=r["file_ext"],
            file_url=r["file_url"],
            preview_url=r["preview_url"],
            sample_url=r["sample_url"],
            jpeg_url=r["jpeg_url"],
            rating=r["rating"],
            file_size=r["file_size"],
            sample_file_size=r["sample_file_size"],
            jpeg_file_size=r["jpeg_file_size"],
            parent_id=r["parent_id"],
            width=r["width"],
            height=r["height"]
        )
        return image