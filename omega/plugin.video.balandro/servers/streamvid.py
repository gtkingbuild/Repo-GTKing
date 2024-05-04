# -*- coding: utf-8 -*-

import re

from platformcode import logger
from core import httptools, scrapertools

from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    resp = httptools.downloadpage(page_url)
    if resp.code == 404 or 'Not Found' in resp.data:
        return "Archivo inexistente ó eliminado"

    data = resp.data

    jdata = scrapertools.find_single_match(data, "<script type=[\"']text/javascript[\"']>\s*;?(eval.*?)</script>")

    unpacked = jsunpack.unpack(jdata)

    matches = re.compile('src:"([^"]+)"', re.DOTALL).findall(unpacked)

    for url in matches:
        video_urls.append(['m3u', url])

    return video_urls
