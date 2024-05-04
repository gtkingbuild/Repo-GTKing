# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    vid = scrapertools.find_single_match(page_url, "embed/([A-z0-9_-]+)")

    if vid:
        data = httptools.downloadpage('https://api.movcloud.net/stream/' + vid).data

        if '"message":"NOT_FOUND"' in str(data):
            return 'Archivo inexistente ó eliminado'

        url = scrapertools.find_single_match(data, '"file":"([^"]+)')
        if url: video_urls.append(["mp4", url])

    return video_urls
