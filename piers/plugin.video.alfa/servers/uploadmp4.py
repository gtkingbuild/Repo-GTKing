# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector uploadmp4 By Alfa development Group
# --------------------------------------------------------

from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url).data
    if "no longer exists" in data:
        return False, "[uploadmp4] El video ha sido borrado"
    return True, ""


def get_video_url(page_url, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url).data
    video_urls = []
    videos_url = scrapertools.find_multiple_matches(data, 'label":"([^"]+).*?file":"([^"]+)')
    for quality, video in videos_url:
        video_urls.append(["%s [uploadmp4]" %quality, video])

    return video_urls
