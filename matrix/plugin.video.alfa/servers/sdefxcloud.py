# -*- coding: utf-8 -*-
import re
from core import httptools
from core import scrapertools
from core import servertools
from core.item import Item
from lib import jsunhunt
from platformcode import logger

kwargs = {'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'CF': True, 'cf_assistant': False, 'ignore_response_code': True}

def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data
    data = httptools.downloadpage(page_url, **kwargs).data
    if ">404</h1>" in data or 'is invalid' in data:
        return False, "[sdefxcloud] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_url  = ""
    code = scrapertools.find_single_match(data, 'dhYas638H\("([^"]+)"')
    decod = decode(code)
    code = scrapertools.find_single_match(decod, 'dhYas638H\("([^"]+)"')
    decod = decode(code)
    url = scrapertools.find_single_match(decod, '<iframe.*? src="([^"]+)"')
    server = servertools.get_server_from_url(url)
    video_url = servertools.resolve_video_urls_for_playing(server, url)
    if not video_url:
        platformtools.dialog_ok("sdefxcloud: Error", "Error en el servidor: %s" %server)
    return video_url[0]

def decode(code):
    logger.info()
    import base64
    decode = base64.b64decode(code).decode('utf-8')
    decode = base64.b64decode(decode).decode('utf-8')
    return decode

