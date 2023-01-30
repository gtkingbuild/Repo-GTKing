# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector GoUnlimited By Alfa development Group
# --------------------------------------------------------

import re
from core import httptools
from platformcode import logger
from core import scrapertools
from lib import jsunpack


def test_video_exists(page_url):
    logger.info()
    global data
    data = httptools.downloadpage(page_url).data
    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    if "File was deleted" in data\
       or "Page Not Found" in data\
       or data and "|videojs7|" in data:
        return False, "[gounlimited] El video ha sido borrado o no existe"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    packed_data = scrapertools.find_single_match(data, "javascript'>(eval.*?)</script>")
    unpacked = jsunpack.unpack(packed_data)
    patron = "src:([^\]]+),type:video/mp4,res:\d+,label:(\d+)"
    matches = re.compile(patron, re.DOTALL).findall(unpacked)
    for url,quality in matches:
        video_urls.append(['[gounlimited] %s' % quality, url])
    
    return video_urls
