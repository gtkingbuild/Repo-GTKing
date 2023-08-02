# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector pornhub By Alfa development Group
# --------------------------------------------------------

import re
from core import httptools
from core import scrapertools
from platformcode import logger
from core import jsontools as json

kwargs = {'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 0, 'ignore_response_code': True, 'cf_assistant': False}


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    response = httptools.downloadpage(page_url, **kwargs)
    data = response.data
    if not response.sucess or "Not Found" in data or "flagged for  " in data or "Video Disabled" in data or "<div class=\"removed\">" in data or "is unavailable" in data:
        return False, "[pornhub] El fichero no existe o ha sido borrado"
    if "premiumLocked" in data:
        return False, "[pornhub] Cuenta premium"
    return True, ""


def get_video_url(page_url, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    headers = {'Referer': 'https://es.pornhub.com/'}
    data = httptools.downloadpage(page_url, headers=headers, **kwargs).data
    flashvars = scrapertools.find_single_match(data, '(var flashvars.*?)</script>')
    flashvars = flashvars.replace('" + "', '' ).replace("\/", "/")
    videos = scrapertools.find_single_match(flashvars, '"mediaDefinitions":(.*?),"isVertical"')
    crypto = scrapertools.find_multiple_matches(flashvars, "(var\sra[a-z0-9]+=.+?);flash")
    if not crypto:
        JSONData = json.load(videos)
        for elem in JSONData:
            url = elem['videoUrl']
            type = elem['format']
            quality = elem['quality']
            # logger.debug("[%s] %s" %(quality, url))
            if quality and 'validfrom=' in url:
                video_urls.append(["[pornhub] m3u %s" % quality, url])
            video_urls.sort(key=lambda item: int( re.sub("\D", "", item[0])))
            if "get_media" in url:
                video_json = httptools.downloadpage(url, set_tls=True, set_tls_min=True).json
                for video in video_json:
                    url = video['videoUrl']
                    quality = video['quality']
                    video_urls.append(["[pornhub] mp4 %sP" % quality, url])
    else:
        for elem in crypto:
            orden = scrapertools.find_multiple_matches(elem, '\*\/([A-z0-9]+)')
            url= ""
            quality = ""
            for i in orden:
                url += scrapertools.find_single_match(elem, '%s="([^"]+)"' %i)
            quality = scrapertools.find_single_match(url, '/(\d+P)_')
            if quality and 'validfrom=' in url:
                video_urls.append(["[pornhub] m3u %s" % quality, url])
            video_urls.sort(key=lambda item: int( re.sub("\D", "", item[0])))
            # logger.debug("[%s] %s" %(quality, url))
            if "get_media" in url:
                video_json = httptools.downloadpage(url, set_tls=True, set_tls_min=True).json
                for video in video_json:
                    url = video['videoUrl']
                    quality = video['quality']
                    video_urls.append(["[pornhub] mp4 %sP" % quality, url])
    
    return video_urls
