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

forced_proxy_opt = 'ProxySSL'

kwargs = {'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 0, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'ignore_response_code': True, 'cf_assistant': False}


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global server,  data
    server = scrapertools.get_domain_from_url(page_url).split(".")[-2]
    if "send" in server:
        data = httptools.downloadpage(page_url, timeout=20, **kwargs).data
    data = httptools.downloadpage(page_url, **kwargs).data
    if "<h2>WE ARE SORRY</h2>" in data or '<title>404 Not Found</title>' in data:
        return False, "[%s] El fichero no existe o ha sido borrado" %server
    return True, ""


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    try:
        if soup.video.source:
            tipo = soup.video.source['type']    # application/x-mpegURL & video/mp4
        matches  = soup.video.find_all('source', type=tipo)
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

