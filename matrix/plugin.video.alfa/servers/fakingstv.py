# -*- coding: utf-8 -*-

from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    media_url = ""
    data = httptools.downloadpage(page_url).data
    media_url = scrapertools.find_single_match(data, '<source src="([^"]+)"')
    if not media_url:
        media_url = scrapertools.find_single_match(data, '<div class="video-wrapper">.*?<iframe src="([^"]+)"')
        data = httptools.downloadpage(media_url).data
        media_url = scrapertools.find_single_match(data, '<source src="([^"]+)"')
    else:
        data = httptools.downloadpage(page_url).data
        media_url = scrapertools.find_single_match(data, '\'file\': \'([^"]+)\',')
    video_urls = []
    video_urls.append([scrapertools.get_filename_from_url(media_url)[-4:] + " [fakingstv]", media_url])

    return video_urls
