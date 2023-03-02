# -*- coding: utf-8 -*-

from core import httptools, scrapertools, servertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info('url = ' + page_url)
    video_urls = []

    page_url = servertools.normalize_url('vshare', page_url)
    data = httptools.downloadpage(page_url).data

    if 'No longer available!' in data:
        return 'El archivo no existe o ha sido borrado'

    video_urls = extraer_videos(data)

    if len(video_urls) == 0:
        parms = scrapertools.find_multiple_matches(data, '<input type="hidden" name="([^"]+)" value="([^"]+)"')
        if not parms:
            return video_urls

        post = '&'.join([nombre + '=' + valor for nombre, valor in parms])
        post += '&method_free=Proceed+to+video'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = httptools.downloadpage(page_url, post=post, headers=headers).data

        video_urls = extraer_videos(data)

    return video_urls


def extraer_videos(data):
    video_urls = []
    try:
        url, tipo = scrapertools.find_single_match(data, '<source src="([^"]+)".*?type="([^"]+)"')
        video_urls.append([tipo, url + '|verifypeer=false'])
    except:
        pass
    else:
        return video_urls