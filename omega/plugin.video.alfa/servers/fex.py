# -*- coding: utf-8 -*-
# -*- Server Fex -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

from core import httptools
from platformcode import logger

def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    data = httptools.downloadpage(page_url, follow_redirects=False)

    if data.code == 404:
        return False, "[Fex] El archivo no existe o ha sido borrado"

    return True, ""

def get_video_url(page_url, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    data = httptools.downloadpage(page_url, follow_redirects=False, only_headers=True)
    logger.debug(data.headers)
    url = data.headers['location']
    video_urls.append(['Fex', url])
    return video_urls
