# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    id = scrapertools.find_single_match(page_url, "/d/([^$]+)")
    if not id: id = scrapertools.find_single_match(page_url, "api.gofile.io/(.*?)$")

    api_data = httptools.downloadpage('https://api.gofile.io/createAccount').data

    if not '"ok"' in str(api_data):
        return 'El archivo ha sido eliminado o no existe'

    token = scrapertools.find_single_match(str(api_data), '"token":"(.*?)"')
    if not token: return video_urls

    url = 'https://api.gofile.io/getContent?contentId=%s&token=%s' % (id, token)
    data = httptools.downloadpage(url, headers={'Referer': page_url.replace('/api.gofile.io/', '/gofile.io/d/')}).data

    if not '"contents"' in str(data):
        return 'Vídeo no autorizado'

    info =  scrapertools.find_single_match(str(data), '"contents":"(.*?)"')

    for k, v in info.items():
        video_urls.append([v["mimetype"].replace('video/', ''), v['link']])

    return video_urls
