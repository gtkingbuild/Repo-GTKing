# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector tubst By Alfa development Group
# --------------------------------------------------------

from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    response = httptools.downloadpage(page_url)
    if not response.sucess or "Not Found" in response.data or "File was deleted" in response.data or "is no longer available" in response.data:
        return False, "[tubst] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    patron = """source src="([^"]+).*?res\s*='([^']+)"""
    match = scrapertools.find_multiple_matches(data, patron)
    for media_url, calidad in match:
        title = "%s [tubst]" % (calidad)
        video_urls.append([title, media_url, int(calidad)])

    video_urls.sort(key=lambda x: x[2])
    for video_url in video_urls:
        video_url[2] = 0
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
