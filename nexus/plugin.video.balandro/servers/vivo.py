# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] < 3:
    import urllib
else:
    import urllib.parse as urllib


import base64

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    if not 'data-stream=' in data and not "source: '" in data:
        return 'Archivo inexistente ó eliminado'

    stream = scrapertools.find_single_match(data, 'data-stream="([^"]+)')
    if stream:
        try:
            url = base64.b64decode(stream)
            if url: video_urls.append(['mp4', url])
        except:
            pass

    if len(video_urls) == 0:
        stream = scrapertools.find_single_match(data, "source: '([^']+)")
        url = ''
        for x in urllib.unquote(stream):
            b = ord(x) + 47
            if b > 126: url += chr(b - 94)
            else: url += chr(b)

        if url: video_urls.append(['mp4', url])

    return video_urls
