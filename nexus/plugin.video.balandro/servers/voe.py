# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    if "Not found" in data or "File not found" in data or "File is no longer available" in data or "Error 404" in data:
        return "El fichero no existe o ha sido borrado"

    video_srcs = scrapertools.find_multiple_matches(data, r"mp4': '([^']+)'")

    if not video_srcs:
        bloque = scrapertools.find_single_match(data, "sources.*?\}")
        video_srcs = scrapertools.find_multiple_matches(bloque, ': "([^"]+)')

        if not video_srcs:
            if not video_srcs: video_srcs = scrapertools.find_multiple_matches(bloque, ":.*?'(.*?)'")

    for url in video_srcs:
        video_urls.append(['mp4', url])

    return video_urls
