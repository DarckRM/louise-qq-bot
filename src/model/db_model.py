from attr import dataclass


class BooruTag():
    def __init__(self, tag_id: int, origin_name: str, cn_name: str, alter_name: str, producer: str, info: str) -> None:
        self.tag_id: int = tag_id
        self.origin_name: str = origin_name
        self.cn_name: str = cn_name
        self.alter_name: str = alter_name
        self.producer: str = producer
        self.info: str = info

@dataclass
class LouiseBooruImage():
    id: int
    tags: str
    recorded_at: int
    created_at: int
    updated_at: int
    creator_id: int
    author: str
    source: str
    md5: str
    file_ext: str
    file_url: str
    preview_url: str
    sample_url: str
    jpeg_url: str
    rating: str
    file_size: int
    sample_file_size: int
    jpeg_file_size: int
    parent_id: int
    width: int
    height: int
    