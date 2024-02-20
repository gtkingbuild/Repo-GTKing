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
        return 'Archivo inexistente ó eliminado'

    match = scrapertools.find_single_match(data, "<script type='text/javascript'>(.*?)</script>")

    try:
        jdata = jsunpack.unpack(match)
        data = jdata.replace("\\'", "'")

        url = scrapertools.find_single_match(data, '"(https.*?.mp4)"')
    except:
        url = scrapertools.find_single_match(str(data), '"video/mp4".*?"(.*?)"')

    if not url: url = scrapertools.find_single_match(data, '"file":"([^"]+)')

    if not url: url = scrapertools.find_single_match(data, 'src:"([^"]+)')

    if url:
        ext = url[-4:]
        url +=  "|verifypeer=false&referer=%s" % page_url

        video_urls.append([ext,  url])

    return video_urls

