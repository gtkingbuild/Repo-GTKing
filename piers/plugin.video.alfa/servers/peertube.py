# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector Peertube By Alfa development Group
# --------------------------------------------------------

from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    global data
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url)
    if data.code == 404:
        return False, "[Peertube] El archivo no existe o ha sido borrado"
    data = data.json
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    video_info = data["files"]
    for info in video_info:
        video_urls.append(['%s [Peertube]' % (info["resolution"]["label"]), info["fileUrl"]])
    return video_urls
