# -*- coding: utf-8 -*-

import re

from lib import jsunpack

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    headers = {}

    if "|Referer=" in page_url:
        page_url, referer = page_url.split("|")
        referer = referer.replace('Referer=', '')
        headers = {'Referer': referer}

    resp = httptools.downloadpage(page_url, headers=headers)

    if resp.code == 404 or "not found" in resp.data:
        return 'Archivo inexistente ó eliminado'

    data = resp.data

    try:
       enc_data = scrapertools.find_multiple_matches(data, "text/javascript(?:'|\")>(eval.*?)</script>")
       dec_data = jsunpack.unpack(enc_data[-1])
    except Exception:
       dec_data = data

    sources = 'sources\:\s*\[\{(?:file|src):"([^"]+)"'

    try:
        matches = re.compile(sources, re.DOTALL).findall(dec_data)
        for url in matches:
            video_urls.append(['m3u8', url])
    except Exception:
        pass

    return video_urls
