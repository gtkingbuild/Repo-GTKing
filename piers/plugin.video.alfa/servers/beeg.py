# -*- coding: utf-8 -*-
import re

from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data
    reponse = httptools.downloadpage(page_url)
    data = reponse.data
    if reponse.code == 404 or "not found" in data or "no longer exists" in data or '"sources": [false]' in data:
        return False, "[beeg] El archivo no existe o ha sido borrado"

    return True, ""


def get_video_url(page_url, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    patron = '"fl_cdn_(\d+)": "([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for quality,url in matches:
        url = "https://video.beeg.com/%s" %url
        video_urls.append(['[beeg] %s' %quality, url])
    video_urls.sort(key=lambda item: int( re.sub("\D", "", item[0])))
    return video_urls

