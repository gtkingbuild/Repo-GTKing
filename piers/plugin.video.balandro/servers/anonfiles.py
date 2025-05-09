# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    page_url = page_url.replace('/anonfiles.com/', '/anonfiles.me/')

    data = httptools.downloadpage(page_url).data

    if "Not Found" in data or "File was deleted" in data or "is no longer available" in data:
        return 'Archivo inexistente ó eliminado'
    elif '.zip' in data:
        return 'El archivo está en formato comprimido'

    match = scrapertools.find_multiple_matches(data, 'download-url.*?href="([^"]+)"')

    for url in match:
        url += "|Referer=%s" % page_url
        video_urls.append(['mp4', url])

    return video_urls
