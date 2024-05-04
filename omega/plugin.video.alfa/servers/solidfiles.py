# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector Solidfiles By Alfa development Group
# --------------------------------------------------------

from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global response
    response = httptools.downloadpage(page_url)
    if not response.sucess or "Not Found" in response.data or "File was deleted" in response.data or "is no longer available" in response.data:
        return False, "[streamlare] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    media_url = scrapertools.find_single_match(response.data,'streamUrl":"([^"]+)')
    media_url += '|verifypeer=false'
    video_urls.append(["MP4", media_url])
    return video_urls
