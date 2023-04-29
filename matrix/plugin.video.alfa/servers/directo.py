# -*- coding: utf-8 -*-

from platformcode import logger
from core import scrapertools

kwargs = {'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 0, 'ignore_response_code': True, 
          'timeout': 5, 'cf_assistant': False}


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    invaid_url ="No se ha encontrado un enlace. " \
                "Posiblemente sea un servidor no soportado."

    exists = True if page_url else False
    reason = invaid_url if not exists else ""
    ignore_response_code = False
    if "|ignore_response_code=True" in page_url:
        page_url, ignore_response_code = page_url.split("|")[0], True 
    referer = None
    if "|Referer" in page_url or "|referer" in page_url:
        page_url, referer = page_url.split("|")
        referer = referer.replace('Referer=', '').replace('referer=', '')

    if page_url:
        pattern = r'(?:^[A-Za-z]+://|^/|^[A-Za-z]+:[\\/]+)\S+'
        match = scrapertools.find_single_match(page_url, pattern)
        exists = True if match else False
        reason = "" if exists else "Ruta o enlace inválido."

        if page_url.startswith('http'):
            from core import httptools
            response = httptools.downloadpage(page_url, headers = {'Referer': referer, "Range": "bytes=0-100"}, **kwargs)

            if not ignore_response_code and not response.sucess:
                if response.code != 403:
                    exists = False
                    reason = "El archivo no existe." if response.code == 404 else "Se ha producido un error en el servidor (%s)" % response.code

            else:
                content_type = response.headers.get('Content-Type', '').split(";")[0]
                exists = False if 'text' in content_type else True
                reason = "El enlace no es un video (se encontró tipo %s)." % content_type if not exists else ""

    if not exists and not ignore_response_code:
        reason += " Repórtalo en el foro https://alfa-addon.com\n"
    else:
        reason = "Ha ocurrido un error con este video"

    return exists, reason

# Returns an array of possible video url's from the page_url
def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)

    video_urls = [["%s [directo]" % page_url[-4:], page_url]]

    return video_urls
