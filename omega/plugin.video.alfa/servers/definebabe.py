# -*- coding: utf-8 -*-
import re
from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data
    data = httptools.downloadpage(page_url).data
    if "<h2>WE ARE SORRY</h2>" in data or '<title>404 Not Found</title>' in data:
        return False, "[definebabe] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    id = scrapertools.find_single_match(data, "'video_id': (\d+)")
    url = "https://www.definebabe.com/player/config.php?id=%s" %id
    data = httptools.downloadpage(url).data
    patron = '"video(?:_alt|)_url":"([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for url in matches:
        url = url.replace("\/", "/")
        if "sd" in url: quality="SD"
        if "hd" in url: quality="HD"
        video_urls.append(["[definebabe] %s" %quality, url])
    return video_urls

