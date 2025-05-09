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

    try:
        nid = scrapertools.find_single_match(page_url, 'videobb.(?:ru|site)/v/([A-z0-9_-]+)')
        if not nid: nid = scrapertools.find_single_match(page_url, '/api/source/([A-z0-9_-]+)')
        if not nid: return video_urls

        page_url = 'https://videobb.ru/api/source/' + nid

        resp = httptools.downloadpage(page_url, post='r=&d=videobb.ru')

        data = jsontools.load(resp.data)
        if 'data' not in data or 'success' not in data: return 'Vídeo no encontrado'
        if not data['success']: return 'Archivo inexistente ó eliminado'

        for videos in data['data']:
            if 'file' in videos and 'label' in videos:
                video_urls.append([videos['label'], videos['file']])
    except:
        pass

    return video_urls
