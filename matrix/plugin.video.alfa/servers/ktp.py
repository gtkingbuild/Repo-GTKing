# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector vipporns By Alfa development Group
# --------------------------------------------------------
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

from lib.kt_player import decode

kwargs = {'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'ignore_response_code': True, 'cf_assistant': False}


def test_video_exists(page_url):
    
    response = httptools.downloadpage(page_url, **kwargs)
    if response.code == 404 \
    or "cwtvembeds" in page_url \
    or "Page not Found" in response.data \
    or "File was deleted" in response.data \
    or "video is a private" in response.data \
    or "is no longer available" in response.data\
    or "Embed Player Error" in response.data:
        return False, "[ktplayer] El fichero no existe o ha sido borrado"
    
    global data, license_code
    data = response.data
    license_code = scrapertools.find_single_match(response.data, 'license_code:\s*(?:\'|")([^\,]+)(?:\'|")')
    
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info()
    video_urls = []
    invert = ""
    url = ""
    data = httptools.downloadpage(page_url, **kwargs).data
    if "flashvars.video_url_text" in data: #sunporno
        data = scrapertools.find_single_match(data, '(flashvars.video_url[^\}]+)')
        patron = "(?:flashvars.video_url|flashvars.video_alt_url)\s*=\s*'([^']+)'.*?"
        patron += "(?:flashvars.video_url_text|flashvars.video_alt_url_text)\s*=\s*'([^']+)'"
    elif "video_url_text" in data:
        patron = '(?:video_url|video_alt_url|video_alt_url[0-9]*):\s*(?:\'|")([^\,]+)(?:\'|").*?'
        patron += '(?:video_url_text|video_alt_url_text|video_alt_url[0-9]*_text):\s*(?:\'|")([^\,]+)(?:\'|")'
    else:
        patron = 'video_url:\s*(?:\'|")([^\,]+)(?:\'|").*?'
        patron += 'postfix:\s*(?:\'|")([^\,]+)(?:\'|")'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for url, quality in matches:
        if not "?login" in url and not "signup" in url:
            if "function/" in url:
                url = decode(url, license_code)
            elif url.startswith("/get_file/"):
                url = urlparse.urljoin(page_url, url)
            # url += "|verifypeer=false"
            url += "|Referer=%s" % page_url
            video_urls.append(['[ktplayer] %s' % quality, url])
        if "lq" in quality.lower() or "high" in quality.lower() or "low" in quality.lower():
            invert= "true"
    if invert:
        video_urls.reverse()
    else:
        video_urls.sort(key=lambda item: int( re.sub("\D", "", item[0])))
   
    if not url:
        url = scrapertools.find_single_match(data, '(?:video_url|video_alt_url|video_alt_url[0-9]*):\s*(?:\'|")([^\,]+)(?:\'|").*?')
        video_urls.append(['[ktplayer]', url])
    return video_urls

