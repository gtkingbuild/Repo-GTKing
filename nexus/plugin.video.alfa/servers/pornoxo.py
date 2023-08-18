# -*- coding: utf-8 -*-
import re
from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data
    data = httptools.downloadpage(page_url).data
    if "<h2>WE ARE SORRY</h2>" in data or 'Not Found' in data:
        return False, "[4tube] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    patron = '"src":"([^"]+)","desc":"([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url,quality in matches:
        url = url.replace("\/", "/")
        video_urls.append(['[pornoxo] %s' %quality, url])
    return video_urls[::-1]
