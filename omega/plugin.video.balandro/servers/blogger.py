# -*- coding: utf-8 -*-

import codecs

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    resp = httptools.downloadpage(page_url)

    if resp.code == 404:
        return 'Archivo inexistente ó eliminado'

    data = resp.data

    streams = scrapertools.find_multiple_matches(data, 'play_url":"([^"]+)')

    for strm in streams:
        url = codecs.decode(strm,"unicode-escape")
        video_urls.append(['mp4', url])

    return video_urls
