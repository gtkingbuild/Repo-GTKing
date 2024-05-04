# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    bloque = scrapertools.find_single_match(data, 'file: "([^"]+)')

    for vid in bloque.split(','):
        lbl = scrapertools.find_single_match(vid, '\[([^\]]+)\]')
        if lbl: 
            url = vid.replace('[%s]' % lbl, '')
        else:
            lbl = 'mp4'
            url = vid

        video_urls.append([lbl, url+'|Referer=https://v-s.mobi/'])

    return video_urls
