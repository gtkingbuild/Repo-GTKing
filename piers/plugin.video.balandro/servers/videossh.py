# -*- coding: utf-8 -*-

import os

from platformcode import logger, config
from core import httptools, scrapertools, filetools, jsontools


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    path_server = os.path.join(config.get_runtime_path(), 'servers', 'zplayer.json')
    data = filetools.read(path_server)
    dict_server = jsontools.load(data)

    try:
       notes = dict_server['notes']
    except: 
       notes = ''

    if "out of service" in notes.lower(): return 'Fuera de Servicio'

    data = httptools.downloadpage(page_url).data

    bloque = scrapertools.find_single_match(data, 'sources\s*:\s*\[(.*?)\]')
    matches = scrapertools.find_multiple_matches(bloque, '"(http.*?)"')
    for url in matches:
        ext = 'm3u8' if 'm3u8' in url else 'mp4'
        video_urls.append([ext, url])

    return video_urls
