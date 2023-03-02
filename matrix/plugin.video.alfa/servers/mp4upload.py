# -*- coding: utf-8 -*-

import re

from core import httptools
from core import scrapertools
from lib import jsunpack
from platformcode import logger

def test_video_exists(page_url):
    data = httptools.downloadpage(page_url).data
    if data == "File was deleted" or data == '':
        return False, "[mp4upload] El video ha sido borrado"


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    data = re.sub(r"\n|\r|\t|\s{2}", "", httptools.downloadpage(page_url).data)
    match = scrapertools.find_single_match(data, "<script type='text/javascript'>(.*?)</script>")
    data = jsunpack.unpack(match)
    data = data.replace("\\'", "'")
    media_url = scrapertools.find_single_match(data, '"(https.*?.mp4)"')
    if not media_url:
        media_url = scrapertools.find_single_match(data, '"file":"([^"]+)')
    if not media_url:
        media_url = scrapertools.find_single_match(data, 'src:"([^"]+)')
    ext = media_url[-4:]
    media_url +=  "|verifypeer=false&referer=%s" %page_url
    video_urls = list()
    video_urls.append([ext + " [mp4upload]", media_url])
    return video_urls
