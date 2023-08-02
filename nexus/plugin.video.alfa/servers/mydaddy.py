# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector mydaddy By Alfa development Group
# --------------------------------------------------------

from core import httptools
from core import scrapertools
from platformcode import logger

def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data
    data = httptools.downloadpage(page_url).data
    if "Not Found" in data \
       or "File was deleted" in data \
       or "is no longer available" in data:
        return False, "[mydaddy] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info()
    video_urls = []
    data = httptools.downloadpage(page_url).data
    data = scrapertools.find_single_match(data, 'else(.*?)You can download it')
    data = data.replace("\\", "")
    matches = scrapertools.find_multiple_matches(data, '<source src="([^"]+)" title="([^"]+)"')
    for url,quality in matches:
        if url.startswith("//"):
            url = "https:%s" % url
        if not "Default" in quality:
            quality = quality.replace("p60", "p")
            video_urls.append(["[mydaddy] %s" % quality, url])
    return video_urls

