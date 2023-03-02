# -*- coding: utf-8 -*-
# -*- Server UploadEver -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int


from core import httptools
from core import scrapertools
from platformcode import logger

page = ""

def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global page
    page = httptools.downloadpage(page_url)
    if "File Not Found" in page.data:
        return False, "[UploadEver] El archivo no existe o ha sido borrado"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)

    data = page.data
    post = ""
    block = scrapertools.find_single_match(data, '(?i)<form name="F1"(.*?)</form>')
    matches = scrapertools.find_multiple_matches(block, 'input.*?name="([^"]+)" value="([^"]*)"')
    
    for name, value in matches:
        post += "%s=%s&" % (name, value)

    post += 'adblock_detected=1'

    data = httptools.downloadpage(page_url, post=post, header={'Referer': page_url}).data

    video_urls = []
    media_url = scrapertools.find_single_match(data, '<a class="btn btn-dow".*?href="([^"]+)"')
    filename = scrapertools.get_filename_from_url(media_url)
    video_urls.append(["%s [UploadEver]" % filename, media_url])

    return video_urls

