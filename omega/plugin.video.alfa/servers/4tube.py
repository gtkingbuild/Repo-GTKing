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
    if "<h2>WE ARE SORRY</h2>" in data or 'Not Found' in data:
        return False, "[4tube] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    url = scrapertools.find_single_match(data, '<link rel="canonical" href="([^"]+)"')
    data = httptools.downloadpage(url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    data = scrapertools.find_single_match(data, 'id="download-links">(.*?)</div>')
    id = scrapertools.find_single_match(data, 'data-id="(\d+)"')
    server = scrapertools.find_single_match(data, 'data-name="([^"]+)"')
    label = scrapertools.find_multiple_matches(data, 'data-quality="(\d+)"')
    label.reverse()
    label = '+'.join(label)
    post = {}
    headers = {"origin": "https://www.4tube.com"}
    post_url = "https://token.%s.com/0000000%s/embeds/%s" %(server,id,label)
    data = httptools.downloadpage(post_url, post = post, headers=headers, add_referer=True).data
    patron = '"(\d+)":.*?'
    patron += ',"token":"([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for quality,url in matches:
        video_urls.append(["[4tube] %sp" % quality, url])
    return video_urls
