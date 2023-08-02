# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    resp = httptools.downloadpage(page_url)

    if resp.code == 404:
        return "El archivo no existe o ha sido borrado"
    elif 'Access denied' in resp.data or '/watch_video.php?v=' in resp.data:
        if 'hqq.' in resp.data or 'waaw.' in resp.data or 'netu.' in resp.data:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        return "Acceso restringido al archivo"

    data = resp.data

    sub_server = scrapertools.find_single_match(data, 'file.*?"(.*?)"')
	
    if sub_server:
        vid_id = scrapertools.find_single_match(data, 'var sesz=.*?"(.*?)"')
		
        if vid_id:
            media_url = sub_server + vid_id

            video_urls.append(['mp4', media_url])

    return video_urls
