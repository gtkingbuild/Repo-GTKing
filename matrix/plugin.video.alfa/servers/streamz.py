# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector Streamz By Alfa development Group
# --------------------------------------------------------

import re
from core import httptools
from platformcode import logger
from lib import jsunpack
from core import scrapertools

def test_video_exists(page_url):
    global data
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url)
    if "<b>File not found, sorry!</b" in data.data:
        return False, "[Streamz] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    # pack = scrapertools.find_multiple_matches(data.data, 'p,a,c,k,e,d.*?</script>')
    # for elem in pack:
    pack = scrapertools.find_single_match(data.data, 'p,a,c,k,e,d.*?</script>')
    unpacked = jsunpack.unpack(pack).replace("\\", "" )
    url = scrapertools.find_single_match(unpacked, "src:'([^']+)'")
    url = httptools.downloadpage(url, follow_redirects=False).headers["location"]
    video_urls.append([".mp4 [Streamz]", url])
    return video_urls

