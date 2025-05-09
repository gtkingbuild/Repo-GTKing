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

    if 'The file you were looking for could not be found' in data:
        return 'Archivo inexistente ó eliminado'

    url = scrapertools.find_single_match(data, 'source src="([^"]+)')
    if url:
        video_urls.append(['mp4', url])

    return video_urls
