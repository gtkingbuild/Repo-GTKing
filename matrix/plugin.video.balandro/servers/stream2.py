# -*- coding: utf-8 -*-

from core import httptools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    url= httptools.downloadpage(page_url).url
    url= url.replace("/x", "/getlink-")
    url += ".dll"

    url = httptools.downloadpage(url, headers={"referer": url}, follow_redirects=False).headers["location"]

    if url:
        video_urls.append(['mp4',  url])

    return video_urls

