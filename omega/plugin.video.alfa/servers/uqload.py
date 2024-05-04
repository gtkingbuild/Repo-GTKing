# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector Uqload By Alfa development Group
# --------------------------------------------------------

from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data
    data = httptools.downloadpage(page_url)
    if data.code == 404 or 'File was deleted' in data.data:
        return False, "[Uqload] El archivo no existe o  ha sido borrado"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    patron = 'sources:.?\["([^"]+)"\]'
    matches = scrapertools.find_multiple_matches(data.data, patron)
    for url in matches:
        url = url+'|Referer='+page_url
        video_urls.append(["[uqload]", url])
    return video_urls
