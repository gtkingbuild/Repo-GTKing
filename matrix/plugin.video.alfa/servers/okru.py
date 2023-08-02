# -*- coding: utf-8 -*-

import re

from core import httptools
from core import scrapertools
from platformcode import logger

data = ''
kwargs = {'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 0, 'ignore_response_code': True, 
          'timeout': 5, 'cf_assistant': False}


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data

    if "okru.link" in page_url:
        return True, ""
    data = httptools.downloadpage(page_url, **kwargs).data
    if "copyrightsRestricted" in data or "COPYRIGHTS_RESTRICTED" in data or "LIMITED_ACCESS" in data:
        return False, "[Okru] El archivo ha sido eliminado por violación del copyright"
    elif "notFound" in data or not "u0026urls" in data:
        return False, "[Okru] El archivo no existe o ha sido eliminado"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    global data
    logger.info("url=" + page_url)
    video_urls = []

    if not data: data = httptools.downloadpage(page_url, **kwargs).data
    data = scrapertools.decodeHtmlentities(data).replace('\\', '')
    # URL del vídeo
    for type, url in re.findall(r'\{"name":"([^"]+)","url":"([^"]+)"', data, re.DOTALL):
        url = url.replace("%3B", ";").replace("u0026", "&")
        if "mobile" in type:
            continue
        video_urls.append([type + " [okru]", url])

    if "okru.link" in page_url:
        v = scrapertools.find_single_match(page_url, "t=(\w+)")
        data = httptools.downloadpage("https://okru.link/details.php?v=" + v, **kwargs).json
        url = data.get("file", '')
        video_urls.append(["video [okru]", url])

    return video_urls
