# -*- coding: utf-8 -*-
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re
from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data, m3u
    data = httptools.downloadpage(page_url).data
    m3u = scrapertools.find_single_match(data, 'html5player.setVideoHLS\(\'([^\']+)\'')
    if "Lo sentimos" in data or "has been deleted" in data or "File not found" in data or 'og:video">' in data:
        return False, "[Xvideos] El archivo no existe o ha sido borrado"

    return True, ""


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    data = httptools.downloadpage(m3u).data
    if PY3 and isinstance(data, bytes): data = data.decode()
    patron = 'RESOLUTION=\d+x(\d+),.*?'
    patron += '(hls-.*?.m3u8)'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for quality,url in matches:
        url = m3u.replace("hls.m3u8", url)
        video_urls.append(['[Xvideos] %sp' %quality, url])
    video_urls.sort(key=lambda item: int( re.sub("\D", "", item[0])))
    return video_urls
