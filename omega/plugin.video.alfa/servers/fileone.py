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
        return False, "[fileone] El fichero no existe o ha sido borrado" 
    return True, ""


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    patron  = '<source src=([^\s]+)'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url in matches:
        if not url.startswith("https"):
            url = "https:%s" % url
        video_urls.append(["[fileone]", url])
    return video_urls
