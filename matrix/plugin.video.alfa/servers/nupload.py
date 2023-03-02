# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector nupload By Alfa development Group
# --------------------------------------------------------
import re
from core import httptools
from core import scrapertools
from platformcode import logger
import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int


def test_video_exists(page_url):
    global data
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url)
    if data.code == 404:
        return False, "[nupload] El archivo no existe o ha sido borrado"
    data = data.data
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    server = scrapertools.find_single_match(data, 'file:\s?"([^"]+)"')
    v_id = scrapertools.find_single_match(data, 'var (?:session|sesz)\s?=\s?"([^"]+)"')
    media_url = server + v_id

    video_urls.append(['[nupload]', media_url])

    return video_urls
