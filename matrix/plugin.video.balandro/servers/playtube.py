# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    if 'no longer exists' in data or 'to copyright issues' in data:
        return 'El archivo ha sido eliminado o no existe'

    if 'sources:' not in data:
        packed = scrapertools.find_single_match(data, "eval\((function\(p,a,c,k,e,d.*?)\)\s*</script>")
        if not packed: return video_urls
        data = jsunpack.unpack(packed)

    data = scrapertools.find_single_match(data, 'sources:\s*\[(.*?)\]')

    matches = scrapertools.find_multiple_matches(data, '\{file:"([^"]+)"([^}]*)')
    for url, extra in matches:
        lbl = scrapertools.find_single_match(extra, 'label:"([^"]+)')
        if not lbl: lbl = url[-4:]
        if lbl == '.mpd':
            if platformtools.is_mpd_enabled():
                video_urls.append([lbl, url+'|Referer=https://playtube.ws/', 0, '', True])
        else:
            video_urls.append([lbl, '%s|User-Agent=%s|Referer=%s'%(url, httptools.useragent, page_url)])

    return video_urls
