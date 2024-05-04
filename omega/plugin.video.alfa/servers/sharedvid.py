# -*- coding: utf-8 -*-

from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    patron  = '<source src="([^"]+)" type=\'video/mp4\' label=\'([^\']+)\''
    matches = scrapertools.find_multiple_matches(data, patron)
    for url, quality in matches:
        video_urls.append(["[Sharedvid] %sp" %quality, url])
    return video_urls[::-1]
