# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector playtube By Alfa development Group
# --------------------------------------------------------
import re
import codecs
from core import httptools
from core import scrapertools
from lib import jsunpack
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data, server
    server = scrapertools.get_domain_from_url(page_url).split(".")[-2]
    # server = scrapertools.find_single_match(page_url, '//(?:www.|es.|)([A-z0-9-]+).(?:to|ws|com)')
    data = httptools.downloadpage(page_url)
    if data.code == 404 or "File is no longer available" in data.data or "There is nothing here" in data.data or "Can't create video code" in data.data:
        return False, "[%s] El archivo no existe o ha sido borrado" %server
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    pack = scrapertools.find_single_match(data.data, 'p,a,c,k,e,d.*?</script>')
    unpacked = jsunpack.unpack(pack)
    logger.debug(unpacked)
    url =""
    url = scrapertools.find_single_match(unpacked, 'src="([^"]+)"')# + "|referer=%s" %(page_url)
    if not url:
        url = scrapertools.find_single_match(unpacked, '(?:file|src):"([^"]+)') + "|referer=%s" %(page_url)
    video_urls.append(['m3u8 [%s]' %server, url] )
    return video_urls