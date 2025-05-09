# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

if PY3:
    from urllib.parse import urlencode
else:
    from urllib import urlencode


import re

from platformcode import logger
from core import httptools, scrapertools, servertools
from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)

    video_urls = []

    if '|' in page_url:
        page_url, referer = page_url.split("|", 1)

    data = httptools.downloadpage(page_url).data

    if "File is no longer available as it expired or has been deleted" in data:
        return 'Archivo inexistente ó eliminado'

    try:
       packed = scrapertools.find_single_match(data, "text/javascript'>(eval.*?)\s*</script>")
       unpacked = jsunpack.unpack(packed)

       data = scrapertools.find_single_match(unpacked, "(?is)sources.+?\[(.+?)\]")
    except:
        data = ''

    m3u = scrapertools.find_single_match(data, 'file:"([^"]+)"')

    if m3u:
        url = m3u + "|"
        url += urlencode(httptools.default_headers)

        video_urls.append(['.m3u8', url])

        video_urls = servertools.get_parse_hls(video_urls)

    return video_urls
