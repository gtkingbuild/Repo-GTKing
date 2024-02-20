# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    if "File Not Found" in data:
        return 'Archivo inexistente ó eliminado'

    vid = scrapertools.find_single_match(page_url, "/u/([^$]+)")
    if not vid: vid = scrapertools.find_single_match(page_url, "/l/([^$]+)")

    if vid:
        url = "https://pixeldrain.com/api/file/%s?download" % vid

        video_urls.append(['mp4', url])

    return video_urls
