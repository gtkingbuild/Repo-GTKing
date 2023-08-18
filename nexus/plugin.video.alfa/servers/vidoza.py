# -*- coding: utf-8 -*-

from core import httptools
from core import scrapertools
from platformcode import logger
from core import jsontools
video_urls = []
headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:67.0) Gecko/20100101 Firefox/67.0' }

def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    
    page = httptools.downloadpage(page_url, headers=headers)
    data = page.data
    if not page.sucess:
        return False, "[vidoza] Problemas con el server"
    if "Page not found" in data or "File was deleted" in data or "center text404" in data:
        return False, "[vidoza] El archivo no existe o ha sido borrado"
    elif "processing" in data:
        return False, "[vidoza] El vídeo se está procesando"

    url = scrapertools.find_single_match(data, '<source src="([^"]+)"')
    video_urls.append([".mp4 [vidoza]", url])

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    
    video_urls.reverse()

    return video_urls
