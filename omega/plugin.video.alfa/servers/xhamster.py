# -*- coding: utf-8 -*-
import re
from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    response = httptools.downloadpage(page_url)
    global data
    data = response.data
    if "Video not found" in data or "This video was deleted" in data or "access restricted" in data:
        return False, "[xhamster] El fichero no existe o ha sido borrado"
    return True, ""

def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    patron = '"url":"([^"]+)","fallback":"[^"]+","quality":"(\d+p)",'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url,quality in matches:
        url =  url.replace("\/", "/")
        url += "|Referer=%s&verifypeer=false" %page_url
        video_urls.append(["[xhamster] %s" %quality, url])
    video_urls.sort(key=lambda item: int( re.sub("\D", "", item[0])))
    return video_urls

