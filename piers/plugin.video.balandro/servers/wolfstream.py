# -*- coding: utf-8 -*-

import os

from platformcode import logger, config
from core import httptools, scrapertools, filetools, jsontools


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    path_server = os.path.join(config.get_runtime_path(), 'servers', 'wolfstream.json')
    data = filetools.read(path_server)
    dict_server = jsontools.load(data)

    try:
       notes = dict_server['notes']
    except: 
       notes = ''

    if "out of service" in notes.lower(): return 'Fuera de Servicio'

    data = httptools.downloadpage(page_url).data

    if 'File Not Found' in data:
        return 'Archivo inexistente ó eliminado'

    url = scrapertools.find_single_match(data, '\{src:\s*"([^"]+)')
    if not url: url = scrapertools.find_single_match(data, '\{file:\s*"([^"]+)')

    if url:
        video_urls.append(['m3u8', url])

    return video_urls
