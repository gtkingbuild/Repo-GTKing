# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector Emturbovid By Alfa development Group
# --------------------------------------------------------

import re
from core import httptools
from platformcode import logger
from lib import jsunpack
from core import scrapertools

def test_video_exists(page_url):
    global data, server
    logger.info("(page_url='%s')" % page_url)
    response = httptools.downloadpage(page_url)
    data = response.data
    server = scrapertools.get_domain_from_url(page_url)
    if "<b>File not found, sorry!</b" in data:
        return False, "[Emturbovid] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    patron = "urlPlay\s*=\s*'([^']+)'"
    matches = re.compile(patron,re.DOTALL).findall(data)
    for url in matches:
        url += "|Referer=%s" %server
        video_urls.append(['[Emturbovid]', url])
    return video_urls

