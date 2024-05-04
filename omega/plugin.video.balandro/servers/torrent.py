# -*- coding: utf-8 -*-

from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("server=torrent, la url es la buena")
    if page_url.startswith("magnet:"):
        video_urls = [["magnet: [torrent]", page_url]]
    else:
        video_urls = [[".torrent [torrent]", page_url]]

    return video_urls
