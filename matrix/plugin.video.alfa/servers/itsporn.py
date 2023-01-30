# -*- coding: utf-8 -*-
import re
from core import httptools
from core import scrapertools
from platformcode import logger


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    logger.debug(data)
    url= scrapertools.find_single_match(data, 'data-src-mp4="([^"]+)"')
    logger.debug(url)
    video_urls.append(["[itsporn]", url])
    return video_urls
