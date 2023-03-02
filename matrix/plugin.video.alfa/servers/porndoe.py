# -*- coding: utf-8 -*-
import re
from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data
    data = httptools.downloadpage(page_url).data
    if "<h2>WE ARE SORRY</h2>" in data or '<title>404 Not Found</title>' in data:
        return False, "[porndoe] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    repe = []
    data = httptools.downloadpage(page_url).data
    id = scrapertools.find_single_match(data, '"id": "(\d+)"')
    post = "https://porndoe.com/service/index?device=desktop&page=video&id=%s" %id
    headers = {"Referer": page_url}
    data = httptools.downloadpage(post, headers=headers).data
    patron = '"(\d+)":\{"type":"video","url":"([^"]+)",'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for quality,url in matches:
        url = url.replace("\/", "/")
        if not url in repe:
            repe.extend([url])
            video_urls.append(['%sp' %quality, url])
    return video_urls

