# -*- coding: utf-8 -*-

import re

from platformcode import logger
from core import httptools, scrapertools, servertools
from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)

    video_urls = []

    if '/emb.html?' in page_url:
        _embed = scrapertools.find_single_match(page_url, "(.*?)=")

        if _embed:
            _embed = _embed.replace('/emb.html?', '/embed-')
            _embed = _embed + '.html'

            page_url = _embed

    data = httptools.downloadpage(page_url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if 'File is no longer available as it expired or has been deleted' in data:
        return 'Archivo inexistente ó eliminado'

    file_id = scrapertools.find_single_match(data, "'file_id'.*?'(.*?)'")
    if file_id:
        h = {}

        h ['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0'

        h['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'

        h['Sec-Fetch-User'] = '?1'
        h['Cookie'] = 'aff=2; file_id=%s' % file_id

        data = httptools.downloadpage(page_url, headers=h).data
        data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    try:
        packed = scrapertools.find_single_match(data, "text/javascript'>(eval.*?)\s*</script>")
        unpacked = jsunpack.unpack(packed)
    except:
        unpacked = ''

    if unpacked:
        data_var = scrapertools.find_single_match(unpacked, "(?is)var player\s?=.+?sources.+?\[(.+?)\]")
        matches = scrapertools.find_multiple_matches(str(data_var), 'sources.*?file.*?"(.*?)"')

        if not matches: data_var = str(unpacked)
    else:
        data_var = scrapertools.find_single_match(data, "(?is)var player\s?=.+?sources.+?\[(.+?)\]")
        matches = scrapertools.find_multiple_matches(str(data_var), 'sources:.*?file.*?"(.*?)"')

        if not matches: data_var = str(data)

    if not matches: matches = scrapertools.find_multiple_matches(str(data_var), 'sources:.*?file.*?"(.*?)"')

    for url in matches:
        if not 'master.m3u8' in url: continue

        video_urls.append(['.m3u8', url])

    if video_urls:
        if not (len(video_urls)) == 1:
            return 'Archivo Múltiple No Soportado'

        video_urls = servertools.get_parse_hls(video_urls)

    return video_urls
