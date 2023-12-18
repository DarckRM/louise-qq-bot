import os
import traceback
from typing import List, Optional, Tuple
from DownloadKit import DownloadKit
from DownloadKit.mission import Mission
from config.conf import CONF
from botpy import logger
from src.model.constant import CACHE_PATH, CACHE_PATH_IMAGES

class FileApi():
    def __init__(self, proxy: bool = False) -> None:
        self.dk = DownloadKit(file_exists="skip")
        if proxy:
            proxy_url_http = "http://" + CONF['proxy.host'] + CONF['proxy.port']
            proxy_url_https = "http://" + CONF['proxy.host'] + CONF['proxy.port']
            self.dk.set.proxies(proxy_url_http, proxy_url_https)

    
    async def read_file(self, file_path: str, filename: str) -> Optional[bytes]:
        file_path = CACHE_PATH + file_path
        try:
            if os.path.exists(file_path + filename):
                with open(file_path + filename, "rb+") as f:
                    file_bytes = f.read()
                    return file_bytes
            else:
                logger.error(f"文件不存在: {file_path + filename}")
                return None
        except Exception as e:
            logger.error(f"打开文件异常: {e}\n{traceback.format_exc()}")
            return None
        

        
    def download_images(self, file_urls: List[Tuple], path: str) -> List[Mission]:
        return self.download_multiple_file(file_urls, CACHE_PATH_IMAGES + path)

        
    def download_multiple_file(self, file_urls: List[Tuple], path: str) -> List[Mission]:
        missons: List[Mission] = []
        for file_url in file_urls:
            if len(file_url) == 2:
                missons.append(self.dk.add(file_url=file_url[0], rename=file_url[1], goal_path=path))
            else:
                missons.append(self.dk.add(file_url=file_url, goal_path=path))
        
        self.dk.wait(show=False)
        return missons
        

file_api: FileApi = None

def get_file_api(proxy: bool = False) -> FileApi:
    global file_api
    if not file_api:
        file_api = FileApi(proxy)

    return file_api


if __name__ == "__main__":
    api = get_file_api(True)
    files = [
        ("https://files.yande.re/jpeg/76f7b56e6e42dd9a1d0df28ae1c93730/yande.re%201140043%20ariaridoradora%20ass%20bra%20cameltoe%20kuwayama_chiyuki%20pantsu%20the_idolm%40ster%20the_idolm%40ster_shiny_colors%20thong.jpg", "A"),
        "https://files.yande.re/jpeg/442c7d9aad8bc5b4678ce532d19b5364/yande.re%201140045%20tagme.jpg"
    ]
    api.download_images(files, "sample/")