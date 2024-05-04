# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    headers = [['User-Agent', 'Mozilla/5.0']]

    if '|' in page_url:
        page_url, referer = page_url.split('|', 1)
        headers.append(['Referer', referer])

    if not page_url.endswith('/config'): page_url = scrapertools.find_single_match(page_url, '.*?video/[0-9]+')

    data = httptools.downloadpage(page_url, headers=headers).data

    matches = scrapertools.find_multiple_matches(data, 'mime":"([^"]+)".*?url":"([^"]+)".*?quality":"([^"]+)"')

    for mime, url, qlty in matches:
        video_urls.append(['%s %s' % (mime, qlty), url])

    return video_urls

