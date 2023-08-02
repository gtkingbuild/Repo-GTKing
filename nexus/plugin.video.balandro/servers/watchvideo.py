# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    page_url = page_url.replace('http://', 'https://').replace('://www.', '://')

    data = httptools.downloadpage(page_url).data

    srcs = scrapertools.find_single_match(data, 'sources:\s*\[(.*?)\]')
    if not srcs:
        packed = scrapertools.find_single_match(data, "<script type=[\"']text/javascript[\"']>(eval.*?)</script>")
        if packed:
            unpacked = jsunpack.unpack(packed)

            srcs = scrapertools.find_single_match(unpacked, 'sources:\s*\[(.*?)\]')

    urls = scrapertools.find_multiple_matches(srcs, 'file:"([^"]+)')
    for url in urls:
        lbl = 'm3u8' if url.endswith('.m3u8') else 'mp4'
        video_urls.append([lbl, url])

    return video_urls

