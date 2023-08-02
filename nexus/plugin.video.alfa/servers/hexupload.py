# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector playtube By Alfa development Group
# --------------------------------------------------------
import re
import codecs
from core import httptools
from core import scrapertools
from lib import jsunpack
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data
    data = httptools.downloadpage(page_url)
    if data.code == 404 or "File is no longer available" in data.data or "Archive no Encontrado" in data.data:
        return False, "[hexaupload] El archivo no existe o ha sido borrado" 
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    url = scrapertools.find_single_match(data, 'b4aa.buy\("([^"]+)"')
    import base64
    url = base64.b64decode(url).decode('utf-8')
    video_urls.append(['[hexaupload] .mp4' , url])
    return video_urls