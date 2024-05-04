# -*- coding: utf-8 -*-

import re

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    if 'File does not exist on this server' in data:
        return 'Archivo inexistente ó eliminado'
    elif 'File has expired and does not exist anymore on this server' in data:
        return 'Archivo inexistente ó eliminado'

    match = re.search('(.+)/v/(\w+)/file.html', page_url)
    if not match: return video_urls
    domain = match.group(1)

    media_url = scrapertools.find_single_match(data, 'getElementById\(\'dlbutton\'\).href\s*=\s*(.*?);')
    numbers = scrapertools.find_single_match(media_url, '\((.*?)\)')
    if not numbers: return video_urls

    url = media_url.replace(numbers, "'%s'" % eval(numbers))
    url = eval(url)

    mediaurl = '%s%s' % (domain, url)
    extension = "." + mediaurl.split('.')[-1]
    video_urls.append([extension, mediaurl])

    return video_urls
