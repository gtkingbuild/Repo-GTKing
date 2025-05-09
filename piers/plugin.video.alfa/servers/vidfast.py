# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector vidfast By Alfa development Group
# --------------------------------------------------------
import re
from core import httptools, jsontools
from core import scrapertools
from platformcode import logger

video_urls = []


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    subtitles = ""
    response = httptools.downloadpage(page_url)
    global data
    data = response.data
    if not response.sucess or "Not Found" in data or "File was deleted" in data or "is no longer available" in data:
        return False, "[vidfast] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    referer = 'https://vidfast.co'
    new_url = scrapertools.find_single_match(data, 'sources: \[{file:"([^"]+)"')
    new_data = httptools.downloadpage(new_url, headers={"referer": referer}).data
    patron = 'RESOLUTION=(\d+x\d+).*?URI="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(new_data)
    for res, url in matches:
        url = url.replace("iframes", "index")
        media_url = url + "|referer=%s" % referer
        video_urls.append(["%s [vidfast]" % (res), media_url])

    return video_urls
