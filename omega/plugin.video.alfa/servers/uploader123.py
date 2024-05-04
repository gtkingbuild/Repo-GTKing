# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector Uploader123 By Alfa development Group
# --------------------------------------------------------
from core import httptools
from core import scrapertools
from platformcode import logger

def test_video_exists(page_url):
    logger.info()
    
    global response
    response = httptools.downloadpage(page_url)

    if '/index.html' in response.url:
        return False, "[Uploader123] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info()
    video_urls = []
    data = response.data
    url = scrapertools.find_single_match(data, r'file\s*:\s*"([^"]+)",')
    ext = scrapertools.find_single_match(data, r'type\s*:\s*"([^"]+)",')
    if url:
        video_urls.append([".%s [Uploader123]" % ext, url])
    return video_urls