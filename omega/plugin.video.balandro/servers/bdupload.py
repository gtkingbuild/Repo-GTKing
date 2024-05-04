# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger

# Funciona para descargar el vídeo pero falla para reproducir (no siempre)


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    # ~ data = httptools.downloadpage(page_url).data
    # ~ logger.debug(data)
    # ~ if "Archive no Encontrado" in data:
        # ~ return 'El fichero ha sido borrado'

    page_url = page_url.replace('bdupload.info', 'bdupload.asia')

    post = 'op=download2&id=%s&rand=&referer=&method_free=&method_premium=' % page_url.split('/')[-1]
    data = httptools.downloadpage(page_url, post = post).data

    videourl = scrapertools.find_single_match(data, "window.open\('([^']+)").replace(" ","%20")
    if videourl:
        # ~ if 'fs30.indifiles.com' in videourl: return 'Vídeo no disponible'
        video_urls.append(["mp4", videourl])

    return video_urls
