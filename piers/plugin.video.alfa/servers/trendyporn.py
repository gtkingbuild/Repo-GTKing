# -*- coding: utf-8 -*-
from core import httptools
from core import scrapertools
from platformcode import logger

def test_video_exists(page_url):
    logger.info()
    global data
    data = httptools.downloadpage(page_url).data
    if "File was deleted" in data\
       or "not Found" in data:
        return False, "[%s] El video ha sido borrado o no existe" % "trendyporn"
    return True, ""


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    url = scrapertools.find_single_match(data, 'src:\s"([^"]+)"')
    video_urls.append([".mp4" , url])
    return video_urls

