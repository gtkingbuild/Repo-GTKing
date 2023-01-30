# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector pornhub By Alfa development Group
# --------------------------------------------------------

import re
from core import httptools
from core import scrapertools
from platformcode import logger

def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    response = httptools.downloadpage(page_url, set_tls=True, set_tls_min=True)
    data = response.data
    if not response.sucess or "Not Found" in data or "flagged for  " in data or "Video Disabled" in data or "<div class=\"removed\">" in data or "is unavailable" in data:
        return False, "[pornhub] El fichero no existe o ha sido borrado"
    if "premiumLocked" in data:
        return False, "[pornhub] Cuenta premium"
    return True, ""


def get_video_url(page_url, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    headers = {'Referer': page_url}
    url= ""
    data = httptools.downloadpage(page_url, headers=headers, set_tls=True, set_tls_min=True).data
    data = scrapertools.find_single_match(data, '<div id="player"(.*?)</script>')
    data = data.replace('" + "', '' )
    videourl = scrapertools.find_multiple_matches(data, 'var media_\d+=([^;]+)')
    for elem in videourl:
        orden = scrapertools.find_multiple_matches(elem, '\*\/([A-z0-9]+)')
        url= ""
        for i in orden:
            url += scrapertools.find_single_match(data, '%s="([^"]+)"' %i)
        if "master.m3u8" in url and not "K," in url and not "get_media" in url:
            quality = scrapertools.find_single_match(url, '(\d+P)_')
            video_urls.append(["[pornhub] %s" % quality, url])
    video_urls.sort(key=lambda item: int( re.sub("\D", "", item[0])))
    return video_urls


