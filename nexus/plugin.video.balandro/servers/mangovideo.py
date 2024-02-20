# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


servers = {'1': 'http://www.mangovideo.pw/contents/videos/',
          '7': 'http://server9.mangovideo.pw/contents/videos/',
          '8': 'http://s10.mangovideo.pw/contents/videos/',
          '9': 'http://server2.mangovideo.pw/contents/videos/',
          '10': 'http://server217.mangovideo.pw/contents/videos/',
          '11': 'http://234.mangovideo.pw/contents/videos/',
          '12': 'http://98.mangovideo.pw/contents/videos/',
          '13': 'http://68.mangovideo.pw/contents/videos/',
          '14': 'http://183.mangovideo.pw/contents/videos/',
          '15': 'http://45.mangovideo.pw/contents/videos/',
          '16': 'https://46.mangovideo.pw/contents/videos/',
          '18': 'https://60.mangovideo.pw/contents/videos/',
          '19': 'https://new.mangovideo.pw/contents/videos/'
          }


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    resp = httptools.downloadpage(page_url)

    if not resp.sucess or 'Not Found' in resp.data or 'File was deleted' in resp.data or 'is no longer available' in resp.data:
        return 'Archivo inexistente ó eliminado'

    matches = scrapertools.find_multiple_matches(resp.data, 'function/0/https://mangovideo.pw/get_file/(\d+)/\w+/(.*?.mp4)')

    url = ''

    for server, url in matches:
        server = servers.get(server, server)
        url = server + url

    if url:
        video_urls.append(['mp4', url])

    return video_urls

