# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    if "Not Found" in data or "File was deleted" in data or "is no longer available" in data:
        return 'El archivo no existe o ha sido borrado'

    match = scrapertools.find_multiple_matches(data, 'download-url.*?href="([^"]+)"')
    for url in match:
        url += "|Referer=%s" % page_url
        video_urls.append(['mp4', url])

    return video_urls
