# -*- coding: utf-8 -*-

from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    response = httptools.downloadpage(page_url)
    if response.code == 404 or "Not Found" in response.data:
        return False, "[Youporn] El archivo no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    url = scrapertools.find_single_match(page_url, '/(\d+)/')
    url = "https://www.youporn.com/api/video/media_definitions/%s" % url
    data= httptools.downloadpage(url).data
    patron  = '"quality":"([^"]+)","format":"mp4","videoUrl":"([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for quality, url in matches:
        url =  url.replace("\/", "/").replace("\\u0026", "&")
        logger.debug(url)
        video_urls.append(["[youporn] %sp" %quality, url])
    return video_urls[::-1]

