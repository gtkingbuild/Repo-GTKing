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
import base64


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data, server
    server = scrapertools.get_domain_from_url(page_url).split(".")[-2]
    # server = scrapertools.find_single_match(page_url, 'www.([A-z0-9-]+).com')
    data = httptools.downloadpage(page_url).data
    if "<h2>WE ARE SORRY</h2>" in data or 'Video Not found' in data:
        return False, "[%s] El fichero no existe o ha sido borrado" % server
    return True, ""


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    encode = scrapertools.find_single_match(data,"window.INITIALSTATE =\s+'([^']+)'")
    decode = base64.b64decode(encode).decode('utf-8')
    decode = urlparse.unquote(decode)
    label = scrapertools.find_multiple_matches(decode, '"label":"p(\d+)"')
    label = label[::-1]
    label = '+'.join(label)
    id = scrapertools.find_single_match(decode,'"mediaId":(\d+),')
    post = {}
    headers = {"origin":"https://www.%s.com" %server}
    post_url = "https://token.%s.com/%s/embeds/%s" %(server,id,label)
    data = httptools.downloadpage(post_url, post = post, headers=headers, add_referer=True).data
    patron = '"(\d+)":.*?'
    patron += ',"token":"([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for quality,url in matches:
        video_urls.append(["[%s] %sp" % (server,quality), url])
    return video_urls
