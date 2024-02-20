# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    if 'no longer exists' in data or 'to copyright issues' in data or "We can't find the file" in data:
        return 'Archivo inexistente ó eliminado'

    if 'sources:' not in data:
        packed = scrapertools.find_single_match(data, "eval\((function\(p,a,c,k.*?)\)\s*</script>")
        if not packed:
            return video_urls

        data = jsunpack.unpack(packed)

    data = scrapertools.find_single_match(data, 'sources:\s*\[(.*?)\]')

    matches = scrapertools.find_multiple_matches(data, '"(http[^"]+)"')
    for url in matches:
        extension = scrapertools.get_filename_from_url(url)[-4:]

        if extension == '.mpd':
            video_urls.append(['mpd', url])
        else:
            video_urls.append([extension, url])

    return video_urls
