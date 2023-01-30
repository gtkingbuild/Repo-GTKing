# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector icedrive By Alfa development Group
# --------------------------------------------------------
import re
from core import httptools
from core import scrapertools
from platformcode import logger
import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int


# def test_video_exists(page_url):
    # global data
    # logger.info("(page_url='%s')" % page_url)
    # data = httptools.downloadpage(page_url).data
    # if data.code == 404:
        # return False, "[icedrive] El archivo no existe o ha sido borrado"

    # return True, ""




def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    url = scrapertools.find_single_match(data,'data-file-id="([^"]+)"')
    url = "https://icedrive.net/dashboard/ajax/get?req=public-download&id=file-%s" %url
    data = httptools.downloadpage(url).data
    url = scrapertools.find_single_match(data,'"error":false,"urls":\["([^"]+)"')
    url = url.replace("\/", "/")
    logger.debug(url)
    video_urls.append(['MP4 [icedrive]', url])
    return video_urls

