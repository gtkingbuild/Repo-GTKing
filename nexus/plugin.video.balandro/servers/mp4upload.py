# -*- coding: utf-8 -*-

import re

from core import httptools, scrapertools
from platformcode import logger
from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if data == "File was deleted" or data == '':
        return "El video ha sido borrado"

    match = scrapertools.find_single_match(data, "<script type='text/javascript'>(.*?)</script>")
    data = jsunpack.unpack(match)
    data = data.replace("\\'", "'")

    url = scrapertools.find_single_match(data, '"(https.*?.mp4)"')

    if not url:
        url = scrapertools.find_single_match(data, '"file":"([^"]+)')

    if not url:
        url = scrapertools.find_single_match(data, 'src:"([^"]+)')

    if url:
        ext = url[-4:]
        url +=  "|verifypeer=false&referer=%s" % page_url

        video_urls.append([ext,  url])

    return video_urls

