# -*- coding: utf-8 -*-
from core import httptools
from core import scrapertools
from platformcode import logger

def test_video_exists(page_url):
    logger.info()
    data = httptools.downloadpage(page_url).data
    if "not found" in data:
        return False, "[noodlemagazine] El video ha sido borrado o no existe"
    return True, ""

def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).json
    
    for elem in  data["sources"]:
        url = elem["file"]
        quality = elem["label"]
        video_urls.append(["%s" %quality, url])
    return video_urls[::-1] 

