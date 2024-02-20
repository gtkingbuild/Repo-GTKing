# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    headers = {}
    if url_referer: headers['Referer'] = url_referer

    data = httptools.downloadpage(page_url, headers=headers).data

    if 'https://cdn.staticmoly.me/notice.php?' in data:
        return 'Archivo inexistente ó eliminado'

    packed = scrapertools.find_single_match(data, "<script type=[\"']text/javascript[\"']>(eval.*?)</script>")

    if packed: data = jsunpack.unpack(packed)

    bloque = scrapertools.find_single_match(data, 'sources:\s*\[(.*?)\]')

    matches = scrapertools.find_multiple_matches(bloque, '\{(.*?)\}')

    for vid in matches:
        url = scrapertools.find_single_match(vid, 'file:"([^"]+)')
        lbl = scrapertools.find_single_match(vid, 'label:"([^"]+)')
        if not lbl: lbl = url[-4:]

        if url:
            video_urls.append([lbl, url + '|Referer=https://vidmoly.me/'])

    return video_urls
