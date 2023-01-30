# -*- coding: utf-8 -*-

from core import httptools, scrapertools, jsontools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    try:
        bloque = scrapertools.find_single_match(data, '"sources":\s*(\[.*?\])')
        if not bloque: return video_urls

        data_json = jsontools.load(bloque)

        for vid in sorted(data_json, key=lambda x: (x['height'], x['width']) if 'height' in x else (0, 0)):
            if 'type' in vid and vid['type'].startswith('audio/'): continue

            url = vid['file']

            tit = 'm3u8' if url.endswith('.m3u8') else 'mp4'
            if 'label' in vid: tit += ' %s' % vid['label']
            if 'width' in vid and 'height' in vid: tit += ' %sx%s' % (vid['width'], vid['height'])

            video_urls.append([tit, url])
    except:
        pass

    return video_urls
