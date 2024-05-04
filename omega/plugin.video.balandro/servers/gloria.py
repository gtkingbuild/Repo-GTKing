# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    matches = scrapertools.find_multiple_matches(data, '<source([^>]+)')

    for vid in matches:
        src = scrapertools.find_single_match(vid, ' src="([^"]+)')
        if src.startswith('/'): src = 'https://gloria.tv' + src
        src = src.replace('&amp;', '&')
        if not src: continue

        lbl = 'm3u8' if src.endswith('m3u8') else 'mp4'

        qlty = scrapertools.find_single_match(vid, '&quot;width&quot;:(\d+),&quot;height&quot;:(\d+)')
        if qlty: lbl += ' %sx%s' % (qlty[0], qlty[1])

        video_urls.append([lbl, src])

    return video_urls
