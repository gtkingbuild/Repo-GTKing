# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)

    data = httptools.downloadpage(page_url).data

    if "File Not Found" in data:
        return 'Archivo inexistente ó eliminado'

    url_redirect = scrapertools.find_single_match(data, '<iframe src="([^"]+)"')
    if not url_redirect: return []

    data = httptools.downloadpage(url_redirect).data

    if "We're sorry, this video is no longer available" in data:
        return 'Archivo inexistente ó eliminado'

    url = scrapertools.get_match(data, '{file:"([^"]+)"')
    video_url = "%s|Referer=%s" % (url, url_redirect)
    video_urls = [[scrapertools.get_filename_from_url(url)[-4:], video_url]]

    return video_urls
