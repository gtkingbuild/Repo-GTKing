# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector Megaup By Alfa development Group
# --------------------------------------------------------

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int


from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data
    data = httptools.downloadpage(page_url).data
    msg_error = scrapertools.find_single_match(data, "<li class='no-side-margin'>([^<]+)</li>")

    if "no longer available!" in msg_error:
        return False, "[Megaup] El fichero no existe o ha sido borrado"
    elif msg_error:
        return False, "[Megaup] %s" % msg_error
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    import time
    logger.info("url=" + page_url)
    video_urls = []
    media_url = ""
    
    ext = scrapertools.find_single_match(data, '<div class="heading-1">([^<]+)')[-4:]
    url = scrapertools.find_single_match(data, "' href='([^']+)'>download now")
    
    if url:
        time.sleep(5.5)
        data_url = httptools.downloadpage(url, follow_redirects=False)
        media_url = data_url.headers.get('location', '')
    
    if media_url:
        video_urls.append(["%s [Megaup]" % ext, media_url])

    return video_urls
