# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    url = scrapertools.find_single_match(data, '<source src="([^"]+)')
    if url:
        video_urls.append(['mp4', url])

    return video_urls