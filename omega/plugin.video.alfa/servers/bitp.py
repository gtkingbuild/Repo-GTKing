# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Alfa addon - KODI Plugin
# Conector para bitporno
# https://github.com/alfa-addon
# ------------------------------------------------------------

from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url).data
    if "not found" in data or "no longer exists" in data or '"sources": [false]' in data:
        return False, "[bitp] El archivo no existe o ha sido borrado"

    return True, ""


def get_video_url(page_url, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    videourl = scrapertools.find_multiple_matches(data, '<source src="([^"]+)".*?label="([^"]+)"')
    scrapertools.printMatches(videourl)
    for scrapedurl, scrapedquality in videourl:
        if "loadthumb" in scrapedurl:
            continue
        scrapedurl = scrapedurl.replace("\\","")
        video_urls.append([scrapedquality + " [bitp]", scrapedurl])
    video_urls.sort(key=lambda it: int(it[0].split("p ", 1)[0]))
    return video_urls

