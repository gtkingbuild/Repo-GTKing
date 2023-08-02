# -*- coding: utf-8 -*-
import re
from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    # global data
    data = httptools.downloadpage(page_url).data
    if "<h2>WE ARE SORRY</h2>" in data or '<title>404 Not Found</title>' in data:
        return False, "[jacquieetmicheltv] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    id = scrapertools.find_single_match(page_url, '/([0-9]+)/')
    url = "https://www.jacquieetmicheltv.net/en/api/video/%s/getplayerurl/" %id
    data = httptools.downloadpage(url).data
    url = scrapertools.find_single_match(data, '"video_settings_url": "([^"]+)"')
    data = httptools.downloadpage(url).data
    patron = '"file":"([^"]+)","label":"([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for url,qualyty in matches:
        video_urls.append(["[jacquieetmicheltv] %s" %qualyty, url])
    return video_urls[::-1]

