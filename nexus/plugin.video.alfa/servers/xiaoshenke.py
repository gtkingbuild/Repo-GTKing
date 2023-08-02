# -*- coding: utf-8 -*-
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

import re
from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url).data
    if "<h2>WE ARE SORRY</h2>" in data or 'Not Found' in data:
        return False, "[xiaoshenke] El fichero no existe o ha sido borrado"
    return True, ""

def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    data = data.replace('\\"', '"')
    data = scrapertools.find_single_match(data, '<video(.*?)</video>')
    matches = scrapertools.find_multiple_matches(data, '<source src="([^"]+)" title="(\d+p)')
    for url,quality in matches:
        if url.startswith("//"):
            url = "https:%s" % url
        video_urls.append(["[xiaoshenke] %sp" % quality, url])
    return video_urls
