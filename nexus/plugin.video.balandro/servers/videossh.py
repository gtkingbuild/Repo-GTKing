# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    bloque = scrapertools.find_single_match(data, 'sources\s*:\s*\[(.*?)\]')
    matches = scrapertools.find_multiple_matches(bloque, '"(http.*?)"')
    for url in matches:
        ext = 'm3u8' if 'm3u8' in url else 'mp4'
        video_urls.append([ext, url])

    return video_urls
