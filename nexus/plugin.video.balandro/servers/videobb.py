# -*- coding: utf-8 -*-

from core import httptools, scrapertools, jsontools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

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
