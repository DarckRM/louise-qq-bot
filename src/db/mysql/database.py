import traceback

from datetime import datetime
from typing import Dict, List
from peewee import DoesNotExist, InterfaceError, MySQLDatabase, IntegerField, Model, CharField, OperationalError, TextField
from playhouse.pool import PooledMySQLDatabase
from playhouse.shortcuts import RetryOperationlError

from botpy import logger

from config.conf import CONF
from src.model.constant import CHINA_TZ
from src.model.db_model import BooruTag, LouiseBooruImage

class RetryMySQLDatabase(RetryOperationlError, MySQLDatabase):
    pass


db: MySQLDatabase = RetryMySQLDatabase(
    database=CONF['db.name'],
    host=CONF['db.host'],
    port=CONF['db.port'],
    user=CONF['db.user'],
    password=CONF['db.password'],
    charset="utf8mb4",
    autorollback=True,
    autoconnect=True,
    stale_timeout=300,
    max_connections=8
)

class DbBooruImages(Model):
    id: int = IntegerField(primary_key=True)
    tags: str = CharField()
    recorded_at: int = IntegerField()
    created_at: int = IntegerField()
    updated_at: int = IntegerField()
    creator_id: int = IntegerField()
    author: str = CharField()
    source: str = TextField()
    md5: str = CharField()
    file_ext: str = CharField()
    file_url: str = TextField()
    preview_url: str = TextField()
    sample_url: str = TextField()
    jpeg_url: str = TextField()
    rating: str = CharField()
    file_size: int = IntegerField()
    sample_file_size: int = IntegerField()
    jpeg_file_size: int = IntegerField()
    parent_id: int = IntegerField()
    width: int = IntegerField()
    height: int = IntegerField()

    class Meta:
        database: MySQLDatabase = db
        db_table = "t_booru_images"


class DbBooruTags(Model):
    tag_id: int = IntegerField(primary_key=True)
    origin_name: str = CharField()
    cn_name: str = CharField()
    alter_name: str = CharField()
    producer: str = CharField()
    info: str = CharField()

    class Meta:
        database: MySQLDatabase = db
        db_table = "t_booru_tags"


class LousieDatabase():
    def __init__(self) -> None:
        self.db: MySQLDatabase = db
        try:
            self.db.connect()
        except Exception as e:
            logger.error(f"无法连接至基础数据库: {e}\n{traceback.format_exc()}")
        
        self.db.create_tables([
            DbBooruImages, DbBooruTags
        ])
    
    def save_booru_image(self, images: List[LouiseBooruImage]) -> int:
        try:
            now: int = int(datetime.now(tz=CHINA_TZ).timestamp())
            db_datas = []
            for p in images:
                if not p:
                    continue

                d: Dict = {
                    "id": p.id,
                    "tags": p.tags,
                    "recorded_at": now,
                    "created_at": p.created_at,
                    "updated_at": p.updated_at,
                    "creator_id": p.creator_id,
                    "author": p.author,
                    "source": p.source,
                    "md5": p.md5,
                    "file_ext": p.file_ext,
                    "file_url": p.file_url,
                    "preview_url": p.preview_url,
                    "sample_url": p.sample_url,
                    "jpeg_url": p.jpeg_url,
                    "rating": p.rating,
                    "file_size": p.file_size,
                    "sample_file_size": p.sample_file_size,
                    "jpeg_file_size": p.jpeg_file_size,
                    "parent_id": p.parent_id,
                    "width": p.width,
                    "height": p.height,
                }
                db_datas.append(d)
            
            DbBooruImages.insert_many(db_datas).on_conflict("IGNORE").execute()
            logger.info(f"写入 t_booru_images 成功: {len(db_datas)} 条记录")
            return len(db_datas)
        except InterfaceError as o_e:
            self.db.connect()
        except Exception as e:
            logger.error(f"写入 t_booru_images 异常: {e}\n{traceback.format_exc()}")
            return 0
    
    
    def get_booru_tag(self, cn_name: str) -> BooruTag:
        try:
            tags: List[DbBooruTags] = DbBooruTags.select().where(
                DbBooruTags.cn_name.contains(cn_name)
            )
            if tags:
                b = tags[0]
                return BooruTag(
                    tag_id=b.tag_id,
                    origin_name=b.origin_name,
                    cn_name=b.cn_name,
                    alter_name=b.alter_name,
                    producer=b.producer,
                    info=b.info
                )
        except InterfaceError as o_e:
            self.db.connect()
        except DoesNotExist as e:
            logger.warn(f"获取 booru_tag 记录不存在: {cn_name}") 
            return None
        except Exception as e:
            logger.error(f"获取 booru_tag 记录异常: {e}\n{traceback.format_exc()}")
            return None


    def list_booru_tag(self) -> List[BooruTag]:
        booru_tags: List[BooruTag] = []
        try:
            db_booru_tags: List[DbBooruTags] = DbBooruTags.select()
            for d in db_booru_tags:
                booru_tags.append(BooruTag(
                    tag_id=d.tag_id,
                    origin_name=d.origin_name,
                    cn_name=d.cn_name,
                    alter_name=d.alter_name,
                    producer=d.producer,
                    info=d.info
                ))
            return booru_tags
        except InterfaceError as o_e:
            self.db.connect()
        except Exception as e:
            logger.error(f"获取 BooruTag 列表失败: {e}\n{traceback.format_exc()}")
            return []

database: LousieDatabase = None

def get_database() -> LousieDatabase:
    global database
    if database:
        return database
    database = LousieDatabase()
    return database

if __name__ == '__main__':
    louise = get_database()
    result = louise.get_booru_tag('神里绫华')
    print(result)