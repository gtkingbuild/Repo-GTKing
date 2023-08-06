# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    if 'embed-' not in page_url:
        page_url = page_url.replace('/uqload.com/', '/uqload.com/embed-')
        page_url = page_url.replace('/uqload.org/', '/uqload.com/embed-')
        page_url = page_url.replace('/uqload.co/', '/uqload.com/embed-')
        page_url = page_url.replace('/uqload.io/', '/uqload.com/embed-')

    if not page_url.endswith('.html'): page_url += '.html'

    data = httptools.downloadpage(page_url).data

    bloque = scrapertools.find_single_match(data, 'sources\s*:\s*\[(.*?)\]')
    matches = scrapertools.find_multiple_matches(bloque, '(http.*?)"')
    for url in matches:
        video_urls.append(['mp4', url+'|Referer=https://uqload.com/'])

    return video_urls
