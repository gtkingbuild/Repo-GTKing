# -*- coding: utf-8 -*-
# -*- Server Uppom -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import re
from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    data = get_source(page_url)

    if "File was deleted" in data or "File Not Found" in data:
        return False, "[Uppom] El video ha sido borrado"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info()
    video_urls = []
    data = httptools.downloadpage(page_url).data
    fid = scrapertools.find_single_match(data, ' name="id" value="([^"]+)"')
    post = "op=download2&id=%s&rand=&referer=%s&method_free=Liberta+Descarga+>>&method_premium=" % (fid, page_url)
    data = httptools.downloadpage(page_url, post=post).data
    media_url = scrapertools.find_single_match(data, '<a href="([^"]+)">http')
    ext = scrapertools.get_filename_from_url(media_url)
    video_urls.append(["%s [Uppom]" % ext, media_url])

    return video_urls
