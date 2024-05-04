# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector PixelDrain By Alfa development Group
# --------------------------------------------------------

from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    global data
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url)
    status = data["headers"].get('success', '')
    if status == False:
        return False, "[PixelDrain] El video ha sido borrado"
    elif not status:
        return False, "[PixelDrain] Error al acceder al video"
    data = data.data
    return True, ""


def get_video_url(page_url, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = list()
    v_id = scrapertools.find_single_match(page_url, "/u/([^$]+)")
    media_url = "https://pixeldrain.com/api/file/%s?download" % v_id
    video_urls.append(["[PixelDrain]", media_url, 0])

    return video_urls
