# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector jottacloud By Alfa development Group
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
    data = httptools.downloadpage(page_url).data
    logger.debug(data)
    if "Unable to retrieve" in data:
        return False, "[jottacloud] El archivo no existe o ha sido borrado"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    url = scrapertools.find_single_match(data,'<form action="([^"]+)"')
    url = "https://www.jottacloud.com%s" %url
    video_urls.append(['MP4 [jottacloud]', url])
    return video_urls

