# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger

from lib.aadecode import decode as aadecode
from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    code = scrapertools.find_single_match(data, '(ﾟωﾟ.*?)</script>')
    if not code: return video_urls
    text_decode = aadecode(code)

    packed = scrapertools.find_single_match(text_decode, "eval\((function\(p,a,c,k.*?)\)$")
    if not packed: return video_urls
    text_decode = jsunpack.unpack(packed)

    bloque = scrapertools.find_single_match(text_decode, 'sources:\s*\[(.*?)\]')

    matches = scrapertools.find_multiple_matches(bloque, '\{(.*?)\}')
    for vid in matches:
        url = scrapertools.find_single_match(vid, '"file":"([^"]+)')
        if not url: continue
        lbl = scrapertools.find_single_match(vid, '"label":"([^"]+)')
        if not lbl: lbl = url[-4:]
        video_urls.append([lbl, url])
        # ~ video_urls.append([lbl, url+'|Referer=https://uploads.mobi/'])

    return video_urls
