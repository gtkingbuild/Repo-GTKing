# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    bloque = scrapertools.find_single_match(data, 'sources\s*:\s*\[(.*?)\]')
    matches = scrapertools.find_multiple_matches(bloque, '(http.*?)"')
    for videourl in matches:
        extension = scrapertools.get_filename_from_url(videourl)[-4:]
        video_urls.append([extension, videourl])

    return video_urls
