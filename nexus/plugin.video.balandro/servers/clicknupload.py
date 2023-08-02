# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)

    video_urls = []

    data = httptools.downloadpage(page_url).data

    if 'File Not Found' in data:
        return 'El archivo no existe o ha sido borrado'

    post = ''

    block = scrapertools.find_single_match(data, '(?i)<Form method="POST"(.*?)</Form>')
    matches = scrapertools.find_multiple_matches(block, 'input.*?name="([^"]+)".*?value="([^"]*)"')

    for name, value in matches:
        post += name + '=' + value + '&'

    post = post.replace("download1", "download2")

    headers = {'Referer': page_url}

    data = httptools.downloadpage(page_url, post=post, headers=headers).data

    url = scrapertools.find_single_match(data, "window.open\('([^']+)")
    if url:
        video_urls.append(["mp4", url])

    return video_urls
