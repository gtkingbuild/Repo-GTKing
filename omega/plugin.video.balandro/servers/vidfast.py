# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    bloque = scrapertools.find_single_match(data, 'sources:\s*\[(.*?)\]')
    url = scrapertools.find_single_match(bloque, '\{file:"([^"]+)"')

    # ~ if url:
        # ~ video_urls.append(['m3u8', url+'|Referer=https://vidfast.co/'])
        # ~ return video_urls

    if url:
        data = httptools.downloadpage(url, headers={'Referer': 'https://vidfast.co/'}).data

        matches = scrapertools.find_multiple_matches(data, 'RESOLUTION=\d+x(\d+).*?(http.*?\.m3u8)')
        if matches:
            for res, url in matches:
                if '/iframes' in url: continue
                video_urls.append([res+'p', url+'|Referer=https://vidfast.co/'])

    return video_urls
