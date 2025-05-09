# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] < 3:
    import urllib
else:
    import urllib.parse as urllib

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    page_url = page_url.replace('http://', 'https://')

    data = httptools.downloadpage(page_url).data

    if 'myvi.ru/player/embed/html/' in page_url:
        page_url = scrapertools.find_single_match(data, '<link rel="canonical" href="([^"]+)')
        if page_url:
            page_url = page_url.replace('myvi.ru/', 'myvi.xyz/').replace('/watch/', '/embed/')
            data = httptools.downloadpage(page_url).data

    bloque = scrapertools.find_single_match(data, 'CreatePlayer\("([^"]+)')

    if not bloque: bloque = scrapertools.find_single_match(data, 'createPlayer\("([^"]+)')
    if not bloque: return video_urls

    data = urllib.unquote(bloque)

    bloques = data.split('\u0026')

    if bloques[0].startswith('v=//'):
        url = bloques[0].replace('v=', 'https:')
    elif bloques[0].startswith('v=http'):
        url = bloques[0].replace('v=', '')
    else:
        url = None

    if url:
        video_urls.append(['mp4', url])

    return video_urls
