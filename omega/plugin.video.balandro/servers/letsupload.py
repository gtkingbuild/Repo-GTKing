# -*- coding: utf-8 -*-

from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    if not '/plugins/mediaplayer/site/' in page_url:
        video_urls.append(['mp4', page_url])

    return video_urls
