# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    url = scrapertools.find_single_match(data, '\{src:\s*"([^"]+)')
    if not url: url = scrapertools.find_single_match(data, '\{file:\s*"([^"]+)')

    if url:
        video_urls.append(['m3u8', url])

    return video_urls
