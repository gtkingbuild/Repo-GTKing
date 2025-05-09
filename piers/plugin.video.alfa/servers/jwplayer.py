# -*- coding: utf-8 -*-

from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url).data
    if "The file you were looking for could not be found" in data:
        return False, "[jwplayer] El archivo ha ido borrado"
    return True, ""


def get_video_url(page_url, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url).data
    video_urls = []
    videourl = scrapertools.find_single_match(data, '<meta property="og:video:secure_url" content="([^"]+)')
    video_urls.append([".MP4 [jwplayer]", videourl])

    return video_urls
