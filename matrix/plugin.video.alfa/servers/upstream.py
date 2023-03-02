# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector Upstream By Alfa development Group
# --------------------------------------------------------

import re
from core import httptools
from core import scrapertools
from platformcode import logger
from lib import jsunpack

page = ''
kwargs = {'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 0, 'ignore_response_code': True, 
          'timeout': 5, 'cf_assistant': False}

def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    global page
    page = httptools.downloadpage(page_url, **kwargs)

    if page.code == 404 or '"title">File Not Found</div>' in page.data \
    or 'player_blank.jpg' in page.data or 'assets/images/image-404.png' in page.data:
        return False, "[upstream] El archivo no existe o  ha sido borrado"

    elif '_msg">File was locked by administrator</div>' in page.data:
        return False, "[upstream] Archivo bloqueado"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    data = page.data
    video_urls = []
    packed = scrapertools.find_single_match(data, "text/javascript'>(eval.*?)\s*</script>")

    if packed:
        data = jsunpack.unpack(packed)

    patron = 'file:"([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    patron = 'image:"([^"]+)"'
    host = httptools.obtain_domain(scrapertools.find_single_match(data, patron), scheme=True).rstrip('/')

    for url_ in matches:
        url = url_
        if not url.startswith('http'):
            url = host + url
        ext = url[-4:]
        if ext == '.srt' or ext == '.jpg':
            continue
        url += '|Referer=%s' % page_url
        video_urls.append(["%s [Upstream]" % ext, url])

    return video_urls
