import os
import traceback
from typing import Any, Callable, Dict, List, Set, Tuple

from DownloadKit.mission import Mission
from src.handler.waitting_session import add_session
from src.model.object import WaitingSession
from src.decorator.servicer import on_command
from src.model.db_model import BooruTag, LouiseBooruImage
from src.db.mysql.database import LousieDatabase, get_database
from src.model.constant import CACHE_PATH, CACHE_PATH_IMAGES
from src.http.http_client import get_http_client

from src.model.enum import FeatureType
from src.service.servicer import Servicer
from botpy import logger
from botpy.message import DirectMessage

from src.utils.file_api import get_file_api
from src.utils.string_tool import contain_chinese

CACHE_YANDE: str = CACHE_PATH_IMAGES + "yande/"

db: LousieDatabase = get_database()


class BooruImage(Servicer):

    def __init__(self) -> None:
        self.feature_map: Dict[str, Tuple[FeatureType, Callable]] = {}
        self.feature_map["yande"] = (FeatureType.SYNC, self._yande)

        self.http_client = get_http_client()
        self.file_api = get_file_api()

    def name(self) -> str:
        return "booru_images"

    @on_command("yande")
    async def invoke(message: DirectMessage) -> bool:
        session = WaitingSession(
            user_id=message.author.id,
            guild_id=message.guild_id,
            message_id=message.id,
            handler="direct_message_handler",
            service="booru_images",
            feature="yande"
        )
        add_session(message.author.id, session)
        await message.reply(content=f"正在请求图片, 请稍后")
        return True

    def get_feature(self, feature_name: str) -> (FeatureType, Callable):
        feature_type, feature = self.feature_map.get(
            feature_name, (None, None))
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

        page_nation: List[int] = [1, 5]
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

        images, image_urls = await self._search_yande_image(url, cn_names, page_nation[0], page_nation[1])

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

        logger.info("开始下载原图")
        self.file_api.download_images(image_urls, "yande/")
        logger.info("已下载完毕")

    async def _search_yande_image(self, url: str, cn_names: List[str], page: int = 1, limit: int = 5) -> (List[Dict], List[Tuple]):
        tags: str = ""
        images: List[Dict] = []
        louise_images: List[LouiseBooruImage] = []

        for cn_name in cn_names:
            tag = default_tag(cn_name) if not contain_chinese(
                cn_name) else db.get_booru_tag(cn_name)
            if not tag:
                continue
            tags += tag.origin_name + '+'
        if len(tags) == 0:
            tags = '*+'
        url = f"{url}tags={tags[:-1]}&limit={limit}&page={page}"
        logger.info(f"请求: {url}")

        results = await self.http_client.url(url).get()

        sample_urls: List[Tuple] = []
        image_urls: List[Tuple] = []
        for r in results:
            louise_images.append(self._build_booru_image(r))
            image_urls.append((r["file_url"], r["md5"]))
            sample_urls.append((r["sample_url"], r["md5"]))

        # 先下载 sample 返回, 然后下载原图
        missions: List[Mission] = self.file_api.download_images(
            sample_urls, "sample/yande/")

        for m in missions:
            image = await self.file_api.read_file("images/sample/yande/", m.file_name)
            if not image:
                continue
            try:
                images.append({
                    "author": r["author"],
                    "tags": r["tags"],
                    "url": r["file_url"][8:],
                    "source": r["source"][8:],
                    "image": image
                })
            except Exception as e:
                logger.error(f"处理 Yande 功能异常: {e}\n{traceback.format_exc()}")

        db.save_booru_image(louise_images)
        return images, image_urls

    async def _handle_yande_result(self, r: Dict):
        image: bytes
        sample_image: bytes

        file_name = f"{r['md5']}.{r['file_ext']} "
        sample_name = f"{r['md5']}.jpg "

        if os.path.exists(CACHE_YANDE + sample_name):
            with open(CACHE_YANDE + sample_name, "rb+") as f:
                sample_image = f.read()
                return sample_image
        else:
            image = await self.http_client.url(r["file_url"]).get_bytes()
            sample_image = await self.http_client.url(r["sample_url"]).get_bytes()

        if not os.path.exists(CACHE_YANDE):
            os.makedirs(CACHE_YANDE)

        with open(CACHE_YANDE + file_name, "wb+") as f:
            f.write(image)
        with open(CACHE_YANDE + sample_name, "wb+") as f:
            f.write(sample_image)

        return sample_image

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


def default_tag(word: str):
    return BooruTag(
        tag_id=0,
        origin_name=word,
        cn_name=word,
        alter_name=word,
        producer="default",
        info="default"
    )
