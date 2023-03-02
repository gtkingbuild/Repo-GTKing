# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector Blogger By Alfa development Group
# --------------------------------------------------------
import re
import codecs
from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data
    data = httptools.downloadpage(page_url)
    if data.code == 404:
        return False, "[blogger] El archivo no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    streams = scrapertools.find_multiple_matches(data.data, 'play_url":"([^"]+)')
    for strm in streams:
        url = codecs.decode(strm,"unicode-escape")
        video_urls.append(['Directo [Blogger]', url])

    return video_urls