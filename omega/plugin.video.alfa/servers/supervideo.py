# -*- coding: utf-8 -*-
from core import httptools
from core import scrapertools
from platformcode import logger
from lib import jsunpack


def test_video_exists(page_url):
    global data
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url).data
    if "File is no longer available as it expired or has been deleted" in data or "File Not Found" in data:
        return False, "[supervideo] El fichero ha sido borrado"
    return True, ""


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    packed = scrapertools.find_single_match(data, 'p,a,c,k,e,d.*?</script>')
    unpack = jsunpack.unpack(packed)
    matches = scrapertools.find_multiple_matches(unpack, 'file:"([^"]+)')
    for url in matches:
        if "supervideo" in url: continue
        qlty = url[-4:]
        video_urls.append(["%s [supervideo]" % qlty, url])
    return video_urls
