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
from bs4 import BeautifulSoup


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data, server
    data = httptools.downloadpage(page_url).data
    server = scrapertools.find_single_match(page_url, '//(?:www.|es.|en.|)([A-z0-9-]+).(?:com|net|nl|sexy|xxx|tv)')
    if "<h2>WE ARE SORRY</h2>" in data or '<title>404 Not Found</title>' in data:
        return False, "[%s] El fichero no existe o ha sido borrado" %server
    return True, ""


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    try:
        matches  = soup.video.find_all('source', type='video/mp4')
    except:
        matches = scrapertools.find_multiple_matches(data, '<source src="([^"]+)" type="video/mp4"')
        for url in matches:
            url += "|Referer=%s" % page_url
            if "justporn" in page_url:
                url = urlparse.urljoin(page_url,url)
            if not url.startswith("http"):
                url = "http:%s" % url
            video_urls.append(["[%s] mp4" %(server), url])
        return video_urls
    for elem in matches:
        url = elem['src']
        url += "|Referer=%s" % page_url
        if "justporn" in page_url:
            url = urlparse.urljoin(page_url,url)
        if not url.startswith("http"):
            url = "http:%s" % url
        video_urls.append(["[%s] mp4" %(server), url])
    return video_urls

