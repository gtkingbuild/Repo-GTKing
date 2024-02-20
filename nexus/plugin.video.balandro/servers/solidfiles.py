# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    resp = httptools.downloadpage(page_url)
    if not resp.sucess or "Not Found" in resp.data or "File was deleted" in resp.data or "is no longer available" in resp.data:
        return 'Archivo inexistente ó eliminado'

    url = scrapertools.find_single_match(resp.data,'streamUrl":"([^"]+)')

    if url:
        video_urls.append(['mp4', url])

    return video_urls
