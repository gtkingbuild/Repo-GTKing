# -*- coding: utf-8 -*-

import re

from lib import jsunpack

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    resp = httptools.downloadpage(page_url)

    if resp.code == 404:
        return 'Archivo inexistente ó eliminado'

    data = resp.data

    enc_data = scrapertools.find_multiple_matches(data, "type='text/javascript'>(eval.*?)?\s+</script>")

    if enc_data:
        dec_data = jsunpack.unpack(enc_data[-1])

        matches = re.compile('sources\:\[\{(?:file|src):"([^"]+)"', re.DOTALL).findall(dec_data)

        for url in matches:
            video_urls.append(['m3u', url])

    return video_urls
