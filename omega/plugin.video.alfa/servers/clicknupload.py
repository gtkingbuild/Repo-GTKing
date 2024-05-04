# -*- coding: utf-8 -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    #from future import standard_library
    #standard_library.install_aliases()
    import urllib.parse as urllib                               # Es muy lento en PY2.  En PY3 es nativo
else:
    import urllib                                               # Usamos el nativo de PY2 que es más rápido

from core import httptools
from core import scrapertools
from platformcode import logger

page = ""

def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global page
    page = httptools.downloadpage(page_url)
    if "File Not Found" in page.data:
        return False, "[Clicknupload] El archivo no existe o ha sido borrado"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)

    data = page.data
    post = ""
    block = scrapertools.find_single_match(data, '(?i)<Form method="POST"(.*?)</Form>')
    matches = scrapertools.find_multiple_matches(block, 'input.*?name="([^"]+)".*?value="([^"]*)"')
    for inputname, inputvalue in matches:
        post += inputname + "=" + inputvalue + "&"

    post = post.replace("download1", "download2")

    data = httptools.downloadpage(page_url, post=post).data

    video_urls = []
    media = scrapertools.find_single_match(data, "onClick=\"window.open\('([^']+)'")
    logger.error(media)
    # Solo es necesario codificar la ultima parte de la url
    url_strip = urllib.quote(media.rsplit('/', 1)[1])
    media_url = media.rsplit('/', 1)[0] + "/" + url_strip

    video_urls.append([scrapertools.get_filename_from_url(media_url)[-4:] + " [clicknupload]", media_url])
    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls

