# -*- coding: utf-8 -*-

import re

from platformcode import logger
from core import httptools, scrapertools, servertools
from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)

    video_urls = []

    if '/emb.html?' in page_url:
        _embed = scrapertools.find_single_match(page_url, "(.*?)=")

        if _embed:
            _embed = _embed.replace('/emb.html?', '/embed-')
            _embed = _embed + '.html'

            page_url = _embed

    data = httptools.downloadpage(page_url).data

    if 'File is no longer available as it expired or has been deleted' in data:
        return 'Archivo inexistente ó eliminado'

    try:
        packed = scrapertools.find_single_match(data, "text/javascript'>(eval.*?)\s*</script>")
        unpacked = jsunpack.unpack(packed)
    except:
        unpacked = ''

    if unpacked:
        data_var = scrapertools.find_single_match(unpacked, "(?is)var player\s?=.+?sources.+?\[(.+?)\]")
        matches = scrapertools.find_multiple_matches(str(data_var), 'sources.*?file.*?"(.*?)"')

        if not matches: data_var = str(unpacked)
    else:
        data_var = scrapertools.find_single_match(data, "(?is)var player\s?=.+?sources.+?\[(.+?)\]")
        matches = scrapertools.find_multiple_matches(str(data_var), 'sources:.*?file.*?"(.*?)"')

        if not matches: data_var = str(data)

    if not matches: matches = scrapertools.find_multiple_matches(str(data_var), 'sources:.*?file.*?"(.*?)"')

    for url in matches:
        video_urls.append(['.m3u8', url])

    if not (len(video_urls)) == 1: return video_urls

    if not 'master.m3u8' in str(video_urls): return video_urls

    video_urls = servertools.get_parse_hls(video_urls)

    return video_urls
