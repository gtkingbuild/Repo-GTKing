# -*- coding: utf-8 -*-

import os

from core import httptools, scrapertools, filetools, jsontools
from platformcode import config, logger


def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
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
    matches = scrapertools.find_multiple_matches(bloque, '(http.*?)"')
    for videourl in matches:
        extension = scrapertools.get_filename_from_url(videourl)[-4:]
        video_urls.append([extension, videourl])

    return video_urls
