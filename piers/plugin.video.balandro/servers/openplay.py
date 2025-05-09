# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger, platformtools


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    bloque = scrapertools.find_single_match(data, '"sources":\s*\[(.*?)\]')
    url = scrapertools.find_single_match(bloque, '"file":\s*"(http[^"]+)')

    # ~ if url:
        # ~ from lib.m3u8server import Client
        # ~ c = Client(url=url, is_playing_fnc=platformtools.is_playing)
        # ~ video_urls.append(['m3u8', c.get_file()])

    if url:
        data = httptools.downloadpage(url).data

        matches = scrapertools.find_multiple_matches(data, 'RESOLUTION=\d+x(\d+).*?\n(url_[^\s]+)')
        if matches:
            url_base = '/'.join(url.split('/')[:-1]) + '/'
            for res, urlres in sorted(matches, key=lambda x: int(x[0])):
                if res+'p' in [x[0] for x in video_urls]: continue
                video_urls.append([res+'p', url_base + urlres])
        else:
            from lib.m3u8server import Client
            c = Client(url=url, is_playing_fnc=platformtools.is_playing)
            video_urls.append(['m3u8', c.get_file()])

    return video_urls
